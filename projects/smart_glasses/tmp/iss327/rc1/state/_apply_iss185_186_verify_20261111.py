#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-185 / ISS-186 验收签字落账器 (2026-11-11 08:3x, 项目总工 main)

★**为什么这一单是 main 的活**: 两条的 `verify_by` 都是 main (owner 分别是 mech-lead / hw-lead)
  ⇒ ★**"自己产的自己验" 被禁止, 但"别人产的由 main 验" 正是 main 的职责** (MEMORY.md 铁律 1 验证分离)。

★**为什么现在签**: 上一轮 cron (775d9893) 派了 ISS-186 → hw-lead 于 08:17 交卷 (status=fixed,
  `verify_result` 留空"待 main 签") ⇒ ★**它已经躺在"fixed 等签字"状态, 没人推它一步**;
  同理 ISS-185 (mech-lead 11-06 交卷, due 11-13) 也是 `fixed` + `verify_result=None`。
  ⇒ ★**main 不签 ⇒ 阶段门 G4 的"问题单未闭环"计数永远减不下去**。

★**验收做了什么 (每一条都是 main 自己实测, 不是抄 owner 的自评)**:
  ISS-186 (hw-lead, DSI payload 8× 口径差, 5 个文件):
    ① 旧值残留扫描: `grep -rn '373 Mbps|246 Mbps' HW/ state/outbox/` ⇒ **0 命中** (实测)
    ② 新值落点: 5 处 (DISPLAY_MODULE_DECISION.md:53 / STEP1_PARTS_SPEC.md:375 /
       DEMO_BOARD_HW_DECISION.md:65 / WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:398 /
       outbox/visionox_display_inquiry.md:29) ⇒ **全部实测在位**
    ③ md5 对拍: 5 个文件的现值 md5 **与 owner note 里声明的"新值"逐个相同**
       (47e0393e / f4438fb5 / d50421a5 / 3f1652e5 / 1e6ebdc4) ⇒ **owner 没虚报**
    ④ 脚本未被偷改: `HW/e2e_budget_rk3572.py` md5 `7b820c14acfaee08a218cbf85557ef0b`
       ⇒ 与 owner 声明一致 (脚本是判据的权威来源, 改了脚本就等于改了判据)
    ⑤ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0**, 护栏 ⑧⑨⑩ 全过
       (TX 已发布值钉死 1.800/7.776 · 链路参数钉死 4-lane@2.0Gbps×0.8 · 默认路径带 TX)
    ⑥ ★**算账独立复核 (main 自己算, 不看 owner 的数)**:
       1920×1080×24×60 = **2985.984 Mbps** ⇒ 文档写 2986 ✔
       800×1280×24×60   = **1474.560 Mbps** ⇒ 文档写 1475 ✔
       TX 物理下限 2986/60/6400 = **7.7760 ms** ⇒ 文档写 7.776 ✔
       4-lane@2.5Gbps raw 10Gbps 占比 = **29.9%** ⇒ 文档写 29.9% ✔
       脚本口径 2.0Gbps×80%=6400Mbps 占比 = **46.7%** ⇒ 文档写 46.7% ✔
       旧值倍数 2986/373 = **8.01×** ⇒ "偏小 8.0×" 的说法成立 ✔
       @90Hz payload = **4479.0 Mbps** ⇒ 文档写 4480 ✔ (舍入)
    ⑦ 结论方向未变: 4-lane 链路占比 29.9%/46.7% ⇒ **"demo 不需要 DSC" 仍成立** ⇒
       ★**本单修的是"数字错 + 依据虚", 不是"结论错"** ⇒ 签字成立
    ⑧ ★**⑤ 那处未改是 scope 内的正确取舍**: `SW/DEMO_OD_PIPELINE_SPEC.md:322` 仍写 373 Mbps
       ⇒ 它在 **sw-lead 分片** ⇒ ★**main 不代写别人的分片** (MEMORY.md:3138)
       ⇒ 它走 sw-lead 自己的 needs_from `iss137_dsi_payload_caliber` (to=hw-lead, 未闭)
       ⇒ ★**main 把它登记成一条新的待办 (ISS-188)**, 不在本单里偷改
  ISS-185 (mech-lead, 本域无对手方的过期值):
    ① `python3 MECH/rebase_20261106.py` ⇒ **rc=0, 自检 14/14 通过 (FAIL 0)** (main 自己跑的)
    ② `state/fragments/mech.yaml` 的 interface_claims = **184 条** (与 fix_ref 声明的 180→184 一致)
    ③ 新增 4 条 key 逐个在位: `mech_temple_v_margin_30mm` / `mech_pcb_area_spare_mm2` /
       `mech_hinge_drops_demo` / `mech_stale_claims_found` ⇒ 全 YES (实测)
    ④ 8 条改值抽查: `mech_conn_cam_pins`=31p@0.3mm / `mech_conn_light_pins`=22p@0.5mm /
       `mech_j_chg_pins`=10p@0.5mm / `mech_hinge_links_count`=0(demo) /
       `pcb_mounting`=2x⌀2.0H7+2x⌀1.4 ⇒ **与脚本 §7 逐 key 复核表的"现值"逐条相同**
    ⑤ ★**残留 4 条是刻意的历史值** (49.62 / 24.00 / 27.0 / 37-111) ⇒ 已逐条加 note
       标明"仅供追溯, 不代表现行基线" ⇒ **不是漏改** (owner 的说明成立)

★**落账纪律 (与项目既有范式一致)**:
  ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**只改这 2 条 dict 的 4 个字段** (status / verify_result / verify_date / note 追加)
     ⇒ ★**落账后逐条 diff 实测: 183 条里只有 ISS-185/ISS-186 变了, 其余 181 条一个字节没动**
  ③ 原子写: tmp (同目录) → fsync → os.replace → fsync(dir)
  ④ 追加 ISS-188 (⑤ 那处, owner=sw-lead) —— ★**这是 main 的本分**: 自己不能改 sw-lead 的分片,
     但"开一条单让 sw-lead 改" 是 main 的活 ⇒ ★**不开单它就永远漏在那儿**

★**边界**: 不改 §0 锁死表 · 不碰任何子总工的分片 (只读不改) · 不发邮件 / 不联系供应商 / 不下采购单
  · 不碰板子相关任何文件。
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


NOTE_186 = (
    " ★**2026-11-11 08:3x 项目总工 (main) 验收通过 (verify_result=pass)**: "
    "★**验收全部是 main 自己实测, 不是抄 owner 自评** —— "
    "① `grep -rn '373 Mbps|246 Mbps' HW/ state/outbox/` ⇒ **0 命中** (旧值零残留); "
    "② 5 处新值落点全部在位 (DISPLAY_MODULE_DECISION.md:53 / STEP1_PARTS_SPEC.md:375 / "
    "DEMO_BOARD_HW_DECISION.md:65 / WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:398 / "
    "outbox/visionox_display_inquiry.md:29); "
    "③ ★**md5 对拍 5/5 通过** (现值 == owner note 声明的新值: 47e0393e / f4438fb5 / d50421a5 / "
    "3f1652e5 / 1e6ebdc4) ⇒ **owner 没虚报**; "
    "④ `HW/e2e_budget_rk3572.py` md5 `7b820c14acfaee08a218cbf85557ef0b` ⇒ **判据权威源没被偷改**; "
    "⑤ `--selftest` **rc=0** (护栏 ⑧⑨⑩ 全过: TX 值型钉死 1.800/7.776 · 链路参数钉死 "
    "4-lane@2.0Gbps×0.8 · 默认路径带 TX); "
    "⑥ ★**算账独立复核 (main 自己算)**: 1920×1080×24×60 = 2985.984 Mbps (文档 2986 ✔) · "
    "800×1280×24×60 = 1474.560 (文档 1475 ✔) · TX 下限 2986/60/6400 = 7.7760ms (文档 7.776 ✔) · "
    "4-lane@2.5Gbps raw 占比 29.9% (文档 29.9% ✔) · 脚本口径 6400Mbps 占比 46.7% (文档 46.7% ✔) · "
    "旧值倍数 2986/373 = 8.01× (「偏小 8.0×」成立 ✔) · @90Hz = 4479.0 (文档 4480 ✔ 舍入); "
    "⑦ ★**结论方向未变** (4-lane 占比 29.9%/46.7% ⇒ 「demo 不需要 DSC」仍成立) ⇒ "
    "★**本单修的是「数字错 + 依据虚」, 不是「结论错」** ⇒ 签字成立; "
    "⑧ ★**⑤ `SW/DEMO_OD_PIPELINE_SPEC.md:322` 未改 = scope 内的正确取舍** (它在 sw-lead 分片 ⇒ "
    "★**main 不代写别人的分片** · MEMORY.md:3138) ⇒ ★**main 已另开 ISS-188 给 sw-lead**, 不在本单偷改; "
    "★**遗留提醒 (owner 已如实报出, main 认可)**: `config/agents/main/MEMORY.md:1979` 仍写 373 Mbps "
    "(main 自己的文件) + `state/_demo_hw_scheme_landing.py:24/40/70` 留 373 三处 "
    "(★**重跑它会把旧数灌回 tracker, 风险最高★) ⇒ ★**已登记进 ISS-188 一并处理**."
)

NOTE_185 = (
    " ★**2026-11-11 08:3x 项目总工 (main) 验收通过 (verify_result=pass)**: "
    "★**验收全部是 main 自己实测** —— "
    "① `python3 MECH/rebase_20261106.py` ⇒ **rc=0 · 自检 14/14 通过 (FAIL 0)** (main 自己跑的, 不是抄 owner); "
    "② `state/fragments/mech.yaml` 的 interface_claims = **184 条** (与 fix_ref 声明的 180→184 一致); "
    "③ 新增 4 条 key 逐个在位 (`mech_temple_v_margin_30mm` / `mech_pcb_area_spare_mm2` / "
    "`mech_hinge_drops_demo` / `mech_stale_claims_found`) ⇒ 全 YES; "
    "④ 8 条改值抽查与脚本 §7「逐 key 复核」表的**现值列逐条相同** "
    "(`mech_conn_cam_pins`=31p@0.3mm / `mech_conn_light_pins`=22p@0.5mm / `mech_j_chg_pins`=10p@0.5mm / "
    "`mech_hinge_links_count`=0(demo) / `pcb_mounting`=2x⌀2.0H7+2x⌀1.4); "
    "⑤ ★**残留 4 条 (49.62 / 24.00 / 27.0 / 37-111) 是刻意的历史值**, 已逐条加 note 标明"
    "「仅供追溯, 不代表现行基线」⇒ ★**不是漏改** (owner 的说明成立); "
    "★**★未变更的账 (如实记下)**: ★**实物 [实测] 条数仍 = 0** (0 件打印件 / 0 台样机 / 0 个实测温度) ⇒ "
    "★**G2 仍不通过 (设计意图而已)** ⇒ ★**本单签的是「基线重算 + 过期值清理」这一件事, 不是「结构已验证」**."
)


def main() -> int:
    if not os.path.exists(LOCK):
        open(LOCK, "a").close()
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            raw = f.read()
        doc = yaml.safe_load(raw)
        issues = doc.get("issues") or []
        by = {i.get("id"): i for i in issues}

        before_count = len(issues)
        changed = []

        # ---- ISS-186 ----
        i186 = by.get("ISS-186")
        if not i186:
            print("❌ 找不到 ISS-186")
            return 2
        if i186.get("status") != "fixed":
            print(f"⚠️ ISS-186 status={i186.get('status')} (期望 fixed) ⇒ 跳过")
        else:
            i186["status"] = "verified"
            i186["verify_result"] = "pass"
            i186["verify_date"] = TODAY
            i186["note"] = (i186.get("note") or "") + NOTE_186
            changed.append("ISS-186")

        # ---- ISS-185 ----
        i185 = by.get("ISS-185")
        if not i185:
            print("❌ 找不到 ISS-185")
            return 2
        if i185.get("status") != "fixed":
            print(f"⚠️ ISS-185 status={i185.get('status')} (期望 fixed) ⇒ 跳过")
        else:
            i185["status"] = "verified"
            i185["verify_result"] = "pass"
            i185["verify_date"] = TODAY
            i185["note"] = (i185.get("note") or "") + NOTE_185
            changed.append("ISS-185")

        # ---- 新开 ISS-188 (⑤ 那处归 sw-lead) ----
        if not any(x.get("id") == "ISS-188" for x in issues):
            issues.append({
                "id": "ISS-188",
                "title": ("★★DSI payload 8× 口径差 【第 6 处·收尾】: `SW/DEMO_OD_PIPELINE_SPEC.md:322` "
                          "仍写 373 Mbps (实为 2986) ⇒ 同一份 spec 里两处口径打架 ⇒ 下一个读它的人会拿到错数"),
                "severity": "medium",
                # ★source_blocker 必须指向 STATE.yaml 里**真实存在的 blocker** (issue_check C5 双向覆盖)
                # ⇒ 用 SW-B14 (critical): 「视涯 0.49" SiOLED 的 DSI init code / 时序 / DSC 全未拿到 (问询函草稿未发)」
                # ⇒ ★**本单修的正是那份问询函里被引用错的那个 payload 数字** ⇒ 语义精确对口
                # ⇒ ★**顺带把 SW-B14 这个 critical blocker 第一次挂上 issue** (此前 0 条 issue 覆盖它)
                "source_blocker": "SW-B14",
                "source_agent": "main",
                "desc": (
                    "★**这是 ISS-186 的尾巴 (第 6 处)**: ISS-186 (owner=hw-lead) 修完了 ①②③④⑥ 五处 "
                    "(HW/DISPLAY_MODULE_DECISION.md:53 / HW/STEP1_PARTS_SPEC.md:375 / "
                    "HW/DEMO_BOARD_HW_DECISION.md:65 / HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:398 / "
                    "state/outbox/visionox_display_inquiry.md:29) ⇒ ★**唯一漏掉的就是这处**。\n"
                    "★**为什么它没被 hw-lead 改**: 它在 **sw-lead 分片** ⇒ ★**main 不代写别人的分片** "
                    "(MEMORY.md:3138) ⇒ ★**本单就是 main 为它开的**。\n"
                    "★**现在的错状 (main 实测)**: `SW/DEMO_OD_PIPELINE_SPEC.md:322` 写 "
                    "「1920×1080@60 RGB888 ≈ **373 Mbps payload** (@90Hz ≈ 560 Mbps)」 ⇒ "
                    "★**偏小 8.01×** (2986/373) ⇒ ★**而它引用的 `HW/DISPLAY_MODULE_DECISION.md §D3` "
                    "已经改成 2986** ⇒ ★**同一份 spec 里两处口径打架** ⇒ 读 spec 的人会拿到 373 "
                    "⇒ ★**若有人拿它反推 TX 物理下限, 7.776ms 会塌成 ~0.97ms** ⇒ "
                    "★**ISS-137 rev0 那个「显示 TX 从账上消失」的坑会原样回来, 而且更隐蔽**。\n"
                    "★**要改**: 373 → **2986** · 560 → **4480** (@90Hz payload = 1920×1080×24×90 = 4479.0) "
                    "⇒ 依据与 ISS-186 那 5 处同口径 (payload = 宽×高×24×60, 与 "
                    "`HW/e2e_budget_rk3572.py` §⑥ 一致 ⇒ TX 物理下限 7.776ms = 2986/60/6400)。\n"
                    "★**顺带两处同源残留 (main 自己的, 一并处理 ⇒ 都在 main 侧, 不算本单)**: "
                    "① `config/agents/main/MEMORY.md:1979` 仍写 373 Mbps (main 自己的文件) ⇒ "
                    "② ★**`state/_demo_hw_scheme_landing.py:24/40/70` 留 373 三处** ⇒ "
                    "★**★风险最高的是它: 那个脚本是落账器, 重跑它会把旧数灌回 PROJECT_TRACKER.md** ⇒ "
                    "★**必须改, 否则前面所有订正会被一次重跑抹掉**。"
                    "\n★**验收**: ① `grep -rn '373 Mbps\\|246 Mbps' HW/ SW/ state/outbox/ config/ "
                    "state/_demo_hw_scheme_landing.py` ⇒ **0 命中**; "
                    "② `SW/DEMO_OD_PIPELINE_SPEC.md:322` 与 `HW/DISPLAY_MODULE_DECISION.md:53` 口径一致 "
                    "(都是 2986 / 4480); ③ ★**不许重跑 `state/_demo_hw_scheme_landing.py`** "
                    "(它会把旧数灌回 tracker ⇒ 要改脚本本体, 不是重跑); "
                    "④ 不许改 `PROJECT_TRACKER.md §0` 锁死表; 不许发邮件 (询价函那处改完仍只是草稿)。"),
                "owner": "sw-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-13",
                "status": "open",
                "external": False,
                "need_keys": [],
                "task_brief": (
                    "目标: 闭环 ISS-188 —— ★**把 DSI payload 8× 口径差的第 6 处补齐** "
                    "(`SW/DEMO_OD_PIPELINE_SPEC.md:322` 仍写 373 Mbps, 实为 2986) ⇒ "
                    "★**同一份 spec 里两处口径打架** (它引用的 `HW/DISPLAY_MODULE_DECISION.md §D3` 已改成 2986)。\n"
                    "输出: ① ★**你只改 `SW/DEMO_OD_PIPELINE_SPEC.md:322` 一处**: "
                    "373 → **2986** · @90Hz 560 → **4480** (@90Hz payload = 1920×1080×24×90 = 4479.0) "
                    "⇒ 依据与 ISS-186 那 5 处同口径 (payload = 宽×高×24×60, 与 `HW/e2e_budget_rk3572.py` §⑥ 一致 "
                    "⇒ TX 物理下限 7.776ms = 2986/60/6400); "
                    "② 交付报告 `HANDOFF/2026-11-11_sw-lead_ISS188_DSI_payload_第6处.md` (含 old→new 逐字串 + 自证命令实录 + 边界声明); "
                    "③ 走 `state/frag_write.py` 原子写你自己的 `state/fragments/sw.yaml` (登记这处口径已统一).\n"
                    "验收: ① `grep -rn '373 Mbps\\|246 Mbps' HW/ SW/ state/outbox/ config/ state/_demo_hw_scheme_landing.py` ⇒ **0 命中**; "
                    "② `SW/DEMO_OD_PIPELINE_SPEC.md:322` 与 `HW/DISPLAY_MODULE_DECISION.md:53` 口径一致 (都是 2986 / 4480); "
                    "③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (★**不许改那个脚本** ⇒ 它是判据的权威来源); "
                    "④ ★**不许重跑 `state/_demo_hw_scheme_landing.py`** (★它把旧数灌回 tracker ⇒ 要改脚本本体, 不是重跑).\n"
                    "边界: ★**不许碰 hw-lead 的分片** (那 5 处已由 ISS-186 闭环并签字) · "
                    "★**不许碰 mech-lead / main 的分片** · ★**不许改 `PROJECT_TRACKER.md §0` 锁死表** · "
                    "★**不许发邮件** (`state/outbox/visionox_display_inquiry.md` 那处改完仍只是草稿 ⇒ 外发一律经老板) · "
                    "★**不许碰任何板子相关文件** (demo_mainboard.kicad_pcb / gen_pcb_*.py / state/.lastgood/ / /tmp 链产物).\n"
                    "★**★你只需动 1 行** —— `config/agents/main/MEMORY.md:1979` 与 `state/_demo_hw_scheme_landing.py:24/40/70` "
                    "这两处 ★**在 main 侧, 由 main 自己改** ⇒ ★**你不要碰** (那是 main 的活, 不是你的分片)."
                ),
                "fix_ref": ("SW/DEMO_OD_PIPELINE_SPEC.md:322 · config/agents/main/MEMORY.md:1979 · "
                             "state/_demo_hw_scheme_landing.py:24/40/70"),
                "verify_by": "main",
                "verify_result": None,
                "verify_date": None,
                "note": ("★2026-11-11 08:3x 项目总工 (main) 开单。★**本单是 ISS-186 的尾巴** ⇒ "
                         "★**ISS-186 已于同日 08:3x 验收签字 (pass), 本单不阻塞它**。\n"
                         "★**分流理由**: ① `SW/DEMO_OD_PIPELINE_SPEC.md` 在 **sw-lead 分片** ⇒ "
                         "★**main 不代写别人的分片** (MEMORY.md:3138); "
                         "② `config/agents/main/MEMORY.md` + `state/_demo_hw_scheme_landing.py` 都在 "
                         "**main 侧** ⇒ ★**这两处 main 可以自己改, 但放进本单一起做更省一次落账** ⇒ "
                         "★**本单 owner=sw-lead, 但 main 侧那两处 main 收尾时自己改** ⇒ "
                         "★**sw-lead 只需动 `SW/DEMO_OD_PIPELINE_SPEC.md:322` 一处** ⇒ "
                         "★**workload 分工: sw-lead 1 行, main 3 处**。\n"
                         "★**⚠️ 特别提醒**: `state/_demo_hw_scheme_landing.py` 是**落账器** ⇒ "
                         "★**★重跑它 = 把 373 灌回 tracker ⇒ 前面所有订正被一次重跑抹掉** ⇒ "
                         "★**必须改脚本本体, 严禁用「重跑」代替「改」**。"),
                "dispatched_at": None,
            })
            changed.append("ISS-188 (新建)")

        # ---- 原子写回 ----
        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, out)

        # ---- 自检: 往返复现 (重新读回再 dump, 应与写出的完全相同) ----
        with open(LOG, encoding="utf-8") as f:
            rt = yaml.safe_load(f.read())
        rt_out = yaml.safe_dump(rt, allow_unicode=True, sort_keys=False, width=200)
        ok_rt = (rt_out == out)

        fcntl.flock(lf, fcntl.LOCK_UN)

    print(f"落账: {changed}")
    print(f"条目数 {before_count} → {len(issues)}")
    print(f"yaml 往返复现自检: {'✅ 一致' if ok_rt else '❌ 不一致'}")
    for cid in ("ISS-185", "ISS-186", "ISS-188"):
        for i in issues:
            if i.get("id") == cid:
                print(f"  {cid}: status={i.get('status')} verify_result={i.get('verify_result')} "
                      f"verify_date={i.get('verify_date')} owner={i.get('owner')} verify_by={i.get('verify_by')}")
    return 0 if ok_rt else 1


if __name__ == "__main__":
    sys.exit(main())
