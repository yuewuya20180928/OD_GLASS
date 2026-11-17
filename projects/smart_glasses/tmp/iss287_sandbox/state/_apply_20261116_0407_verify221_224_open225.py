#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0407_verify221_224_open225.py
★main (moli) 手动清账 + 开新单 · 2026-11-16 04:07 (cron fb67af40 队列自动派活)★

★**为什么做这件事 (★不是例行公事, 是队列止血★)**:
  · ISS-221 (sw-lead) 会话 done@03:59 · ISS-224 (mech-lead) 会话 done@03:58
    ⇒ ★**两个总工名额被"僵尸 fixing"占住** (状态还停在 fixing, 但会话已结束)
    ⇒ ★`state/advance.py` 的 in_flight 规则会让这两个 agent 本轮拿不到任何新活
  · ⇒ 本脚本: ① main 实测验收 ⇒ 把两条落 verified (清掉僵尸占位)
              ② 开 ISS-225 = sw-lead 名额空出来后【唯一不与任何人抢】的活 (SW 侧 md5 基线台账化)

★**ISS-221 / ISS-224 的验收都是 main 自己实跑的 (★不是抄 agent 的交卷报告★)**:
  ISS-221: demo_e2e_budget.py rc=0 / --selftest rc=0 / demo_timing_check.py rc=0 / --selftest rc=0
           / check_demo_panel_spec.py --selftest rc=0 ⇒ 5 项绿; ★**check_demo_panel_spec.py (无参) rc=1**
           ⇒ 红项只有 R6 两行 (网表/脚表 md5 基线过期) ⇒ ★**根因在 ISS-220 落表 (hw-lead, 02:32), 不在 sw-lead**
           ⇒ ★**红的不是 sw-lead 的锅** ⇒ 但它是一条真红 ⇒ 转 ISS-225 (sw-lead 自己收口)
  ISS-224: check_demo_struct_truth.py rc=0 (23/23) / --selftest rc=0 (14/14) / cavity_recalc_check.py rc=0 (20/20)
           / --selftest rc=0 (18/18) / verify_budget.py rc=0 / hw_cross_review_check.py rc=0 (PASS 15/FAIL 16)
           / verify_pack.py rc=0 (46/46) / verify_pack_revb.py rc=0 ⇒ ★**9/9 全绿** ⇒ 可落 verified
"""
import os
import shutil
import datetime as dt
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

BRIEF_225 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**SW 侧因为落表而"恒红"的 md5 基线收口成【台账驱动 + 三方对账】**★ ⇒ 出 ★**(1) `SW/tools/check_demo_panel_spec.py` 的 R6 重锚 + 对账机制 · (2) SW 侧同类硬编码基线全清单 + 逐条处置 · (3) 留痕 · (4) 反向用例 · (5) 交接单 + 分片**★ ⇒ ★**本单不许改 `HW/` 下任何文件**★ ⇒ ★**零外发** ★

★★**现状 (★main 2026-11-16 04:07 实跑, 不是抄交卷报告★)** ★★
· ★**`python3 SW/tools/check_demo_panel_spec.py` → rc=1, 2 项红 (R6)** ★
  - `HW/netlist_v1.csv` (现在 `13f59a43dbd35dc6cb16e897c8c891ab` ≠ 锚点 `c78f991283cc82d56c8e3dd31657c785`)
  - `HW/netlist_v1_pins.csv` (现在 `a600afae493f5a7a6c55f46ad35ac89c` ≠ 锚点 `4814617e22b567d76164e56bc5e39dc8`)
· ★**根因 = ISS-220 (hw-lead) 落表第 1 批 (2026-11-16 02:32) 改了这两个真源** ⇒ ★**锚点过期** ★
· ★**鉴别证据 (★说明"是锚点过期"不是"红灯被调没"★)**: 门禁脚本 `SW/tools/check_demo_panel_spec.py` mtime = 2026-11-15 23:59 ★**早于落表 02:32** ⇒ ★**脚本一个字节没被碰过** ★
· ★**★关键时序风险 (★本单为什么不能只是"追一次 md5"★)**: ★**ISS-223 (hw-lead) 落表第 2 批 (d5 + 补差A) 正在跑 (main 04:07 实测会话仍在跑) ⇒ 它会再改这两个真源** ★ ⇒ ★**你现在把锚点改成 `13f59a43…`, ISS-223 一落表它又恒红** ⇒ ★**⇒ 本单必须做成【台账驱动 + 三方对账】(照抄 MECH 的 C21 机制), 不是【追一次 md5】** ★

★★**交付物 (5 件, 少一件即无效) ★★
① ★**R6 重锚 + 升级成三方对账** ★ ⇒ `SW/tools/check_demo_panel_spec.py` 的 R6: ★**锚点 ↔ 落表台账 ↔ 盘上真源 三方一致** ★ ⇒ ★**机制照抄 `MECH/check_demo_struct_truth.py` 的 C21 (★已存在, 只读参照, 不许改 `MECH/` 下任何文件★)** ★ ⇒ ★**台账来源 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` (ISS-220 落表记录) 或 `HANDOFF/2026-11-16_hw-lead_ISS223_*.md`** ★ ⇒ ★**台账里必须能查到【落表单号 + 文件名 + 新 md5 + 旧 md5】四项** ⇒ ★**只改锚点不落表 = 悄悄换真源 = 红** ★
② ★**SW 侧同根因同类基线全清单 + 逐条处置** ★ ⇒ ★**全项目搜一遍**: 凡在 `SW/` 下硬编码了 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` 的 md5 基线的 (★脚本 + 文档 + 台账★) ⇒ ★**出清单 + 逐条写处置 (台账化 / 保留并说明理由 / 本单不管但登记)** ⇒ ★**不许只修 R6 一处, 留下同根因的下一处恒红** ★
③ ★**留痕** ★ ⇒ ★**写明「这次红 = 【锚点过期】不是【红灯被调没】」+ 根因单号 (ISS-220 / ISS-223) + 新旧 md5 + 复现命令** ⇒ ★**做法照 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1 的「已修复 (留痕)」** ★
④ ★**反向用例 (★`--selftest` 必须全抓到★)** ★ ⇒ ① 盘上真源被换掉而锚点没换 ⇒ 红 ② 锚点改了但台账里查不到该 md5 / 单号 ⇒ 红 ③ 台账里的落表单号改坏 ⇒ 红 ④ 把落表台账那一行删掉 ⇒ 红 ★⇒ ★**少一条反向用例 = 本单无效** ★
⑤ ★**交接单 `HANDOFF/2026-11-16_sw-lead_ISS225_SW侧md5基线台账化.md` (★新建★)** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/sw.yaml` (★必须走 `python3 state/frag_write.py` 原子写★)** ★

★★**边界 (★违反一条即本单无效★) ★★
· ★**不许改** `HW/` 下任何文件 (★网表 / 脚表 / 板 / `.kicad_pro` / 原理图 / BOM 一个字节不许动★) ⇒ ★**落表台账由 hw-lead 写, 本单只读** ★
· ★**不许改** `MECH/` 下任何文件 (★`MECH/check_demo_struct_truth.py` 的 C21 只许只读参照★) ★
· ★**不许改** `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/` / 别人的分片 ★
· ★**不许碰** PCB 布线 / 布局 / 板框 ★
· ★**不许把 `--skip-md5` 设成默认跳过** (★它是既有逃生舱, 默认必须仍校★) ★
· ★**不许硬编码一个"查不到出处"的 md5 当基线** ⇒ ★**锚点值必须 = 盘上真源当前 md5, 且必须在落表台账里查到出处** ⇒ ★**查不到 ⇒ 交卷写明 BLOCKED (缺哪一条), 不许硬写一个数** ★
· ★**板端 [实测] = 0 条** (★板与屏不在本机 ⇒ 标 [实测] 的只允许是"本机脚本 / 本机文件实读"★) ★
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据]) + 查不到必须写降级方案** ★
· ★**不许自签 issue_log** (★status 留给 main 落 verified★) ★

★★**交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★) ★★
```
python3 SW/tools/check_demo_panel_spec.py             # rc=0 (★R6 绿 + R1~R5 一条不许被改红★)
python3 SW/tools/check_demo_panel_spec.py --selftest   # rc=0 (★本单新增反向用例全抓到★)
python3 SW/tools/demo_timing_check.py                 # rc=0 (★ISS-221 的 17 条断言一条不许被改红★)
python3 SW/tools/demo_timing_check.py --selftest      # rc=0
python3 SW/tools/demo_e2e_budget.py                   # rc=0 (★ISS-221 的 demo 真源脚本, 只许读不许改★)
python3 SW/tools/demo_e2e_budget.py --selftest        # rc=0
python3 state/merge.py && python3 state/gate_check.py # rc=0 且 【Q1 交付齐备率】 18/18
```
★**交卷前最后一件事**: ★**再实跑一次 R6** —— 因为 hw-lead 的 ISS-223 可能在本单期间落表 ⇒ ★**交卷那一刻盘上的 md5 才是锚点目标值** ⇒ ★**若 ISS-223 在你交卷之后仍要落 ⇒ 在交卷里写明【锚点会再次过期, 但台账对账机制会自动红, 这是设计】** ★

★★**已知会红、且不归你管的那一盏 (★提前说清, 免得你误修★) ★★
· ★**`MECH/check_demo_struct_truth.py` 在 ISS-223 落表后会按设计变红 (G5b + C21)** ⇒ ★**那不是本单的锅, 更不许为了让 MECH 闸变绿去改 `MECH/`** ⇒ ★**本单只要保证 SW 侧自己的门禁绿, 并在交卷里说明 MECH 闸变红的原因 (交 hw-lead 更新台账 + 锚点)** ★
"""


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {i.get("id"): i for i in issues}

    # ---------- 1. ISS-221 → verified ----------
    i221 = by_id["ISS-221"]
    assert i221.get("status") == "fixing", i221.get("status")
    i221["status"] = "verified"
    i221["verify_by"] = "main"
    i221["verify_date"] = TODAY
    i221["verify_result"] = (
        "★main 2026-11-16 04:07 自测验收 (非抄交卷报告)★\n"
        "· 交付物: ①SW/tools/demo_e2e_budget.py (新建) ②SW/DEMO_OD_TIMING_SPEC.md + SW/DEMO_BOARD_60MS_VERDICT_PLAN.md "
        "③SW/tools/demo_timing_check.py (v1.2, 扩项 17 条断言) ④HANDOFF/2026-11-16_sw-lead_ISS221_demo预算真源.md (B1~B6) "
        "⑤SW/RKNN_BENCH.md §4.1 L273 S9 注记 (md5 ed080fa0→46ac25e1 实测一致, S9=3.0 逐字节未动) ⇒ ★5/5 在盘★\n"
        "· 门禁实跑: demo_e2e_budget.py rc=0 / --selftest rc=0 (9 反向用例+源码污染全红) / demo_timing_check.py rc=0 / "
        "--selftest rc=0 (ISS-221 反例12~15 全抓到) / check_demo_panel_spec.py --selftest rc=0 (8/8) ⇒ ★5 项绿★\n"
        "· ★唯一红项 = `python3 SW/tools/check_demo_panel_spec.py` (无参) rc=1, R6 两行 (网表 c78f9912→13f59a43 / 脚表 "
        "4814617e→a600afae) ⇒ ★根因 = ISS-220 (hw-lead) 2026-11-16 02:32 落表第1批, 锚点过期★ ⇒ ★**该脚本 mtime 2026-11-15 23:59 "
        "早于落表 ⇒ 脚本没被碰过 ⇒ 【锚点过期】不是【红灯被调没】★ ⇒ ★**红的不是 sw-lead 的锅 ⇒ 转 ISS-225 (sw-lead 自己收口)★\n"
        "· 分片: state/fragments/sw.yaml mtime 03:57, artifacts 含 demo_e2e_budget.py / demo_timing_check.py(v1.2) / "
        "HANDOFF ISS221 / RKNN_BENCH.md ⇒ ★分片真落盘★ ⇒ ★**落 verified, 但 R6 那条红已转 ISS-225 继续追, 不算本单欠账★"
    )
    i221["note"] = (i221.get("note") or "") + (
        "\n2026-11-16 04:07 (cron fb67af40 队列自动派活) ★main 实测验收 ⇒ 落 verified★ "
        "⇒ ★同时清掉僵尸 fixing (会话 done@03:59 但状态卡在 fixing ⇒ 占着 sw-lead 名额)★ "
        "⇒ ★R6 恒红那条不是本单造成 ⇒ 转 ISS-225★"
    )

    # ---------- 2. ISS-224 → verified ----------
    i224 = by_id["ISS-224"]
    assert i224.get("status") == "fixing", i224.get("status")
    i224["status"] = "verified"
    i224["verify_by"] = "main"
    i224["verify_date"] = TODAY
    i224["verify_result"] = (
        "★main 2026-11-16 04:07 自测验收 (非抄交卷报告)★\n"
        "· 交付物: ①MECH/HW_CROSS_REVIEW_TRIAGE.md (G1/G1b 重锚 17→16 + §3.1 已修复留痕 + §1 source_ledger) "
        "②MECH/check_demo_struct_truth.py (20→23 组, 新增 C21/C22/G8) ③HANDOFF/2026-11-16_mech-lead_ISS224_门禁锚点再基线.md "
        "(B1~B6) ④state/fragments/mech.yaml (mtime 03:56 真落盘) ⇒ ★4/4 在盘 + 留痕机制齐全★\n"
        "· 门禁实跑: check_demo_struct_truth.py rc=0 (23/23, FAIL 0 组) / --selftest rc=0 (★反向 14/14 全抓到★) / "
        "cavity_recalc_check.py rc=0 (20/20) / --selftest rc=0 (18/18) / verify_budget.py rc=0 / hw_cross_review_check.py rc=0 "
        "(PASS 15 / FAIL 16 —— ★16 条红灯一条没消★) / verify_pack.py rc=0 (46/46) / verify_pack_revb.py rc=0 ⇒ ★**9/9 全绿**★\n"
        "· ★阈值未松: 皮肤 43°C / 端件 60°C / cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00 一个没动★ "
        "· ★4 个受保护脚本 md5 逐字节未变 / `HW/` 一个字节没动★\n"
        "· ★**已知后续 (不追本单账)**: ISS-223 (hw-lead) 落表第 2 批后再改网表/脚表 ⇒ G5b + C21 会【按设计】变红 "
        "⇒ 那是 hw-lead 更新台账 + 锚点的活 (need iss224_hw_landing_must_update_gate_ledger 已登记)★"
    )
    i224["note"] = (i224.get("note") or "") + (
        "\n2026-11-16 04:07 (cron fb67af40 队列自动派活) ★main 实测 9/9 门禁全绿 ⇒ 落 verified★ "
        "⇒ ★同时清掉僵尸 fixing (会话 done@03:58 但状态卡在 fixing ⇒ 占着 mech-lead 名额)★"
    )

    # ---------- 3. 新开 ISS-225 (sw-lead 名额) ----------
    assert "ISS-225" not in by_id, "ISS-225 已存在"
    issues.append({
        "id": "ISS-225",
        "title": "★★[主线内·软件/工具链侧·内部活] SW 侧 md5 基线过期 (`SW/tools/check_demo_panel_spec.py` R6 恒红) ⇒ 重锚 + 落表台账对账 (镜像 MECH C21) + 同根因全清单 + 反向用例 + 留痕",
        "severity": "high",
        "source_blocker": "ISS-221",
        "desc": "★**main 2026-11-16 04:07 实测**: `python3 SW/tools/check_demo_panel_spec.py` → **rc=1, R6 两项红** "
                "(网表 `13f59a43…` ≠ 锚点 `c78f9912…` / 脚表 `a600afae…` ≠ 锚点 `4814617e…`) ★\n"
                "· ★**根因 = ISS-220 (hw-lead) 落表第 1 批 (2026-11-16 02:32) 改了这两个真源 ⇒ 锚点过期** ★\n"
                "· ★**鉴别**: 门禁脚本 mtime 2026-11-15 23:59 早于落表 ⇒ 脚本没被碰过 ⇒ 【锚点过期】不是【红灯被调没】★\n"
                "· ★**★关键时序**: ISS-223 (hw-lead) 落表第 2 批正在跑 ⇒ 会再改这两个真源 ⇒ ★**追一次 md5 等于下一趟又恒红** "
                "⇒ 必须做成【台账驱动 + 三方对账】(照 MECH C21)★\n"
                "· ★**本单 = SW 侧把『锚点过期』这类恒红一次性收口 + 留痕 + 反向用例** ⇒ ★**不是 PCB 布线/布局类, 不是老板级拍板 ⇒ 可派** ★",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 04:07 (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮实跑 `SW/tools/check_demo_panel_spec.py` → rc=1 · R6 两项红** ★\n"
                "★**根因不在 sw-lead** (是 ISS-220 落表打破的旧基线) ⇒ ★**本单不是『补锅』, 是『把这类恒红收口成机制』** ★\n"
                "★**sw-lead 名额的上一条 ISS-221 本轮 04:07 落 verified (main 实测 5 项门禁绿) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改 `HW/` 任何文件 · 不改 `MECH/` 任何文件 · 不碰 PCB 布线布局 · 不写别人分片 · 不发信 · 不自签 issue_log ★",
        "task_brief": BRIEF_225,
        "dispatched_at": None,
    })

    # ---------- 写回 ----------
    shutil.copy2(LOG, LOG + ".bak_20261116_0407_verify221_224_open225")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-221 → verified / ISS-224 → verified / ISS-225 新开 (owner=sw-lead, status=open)")
    print("issues total:", len(log["issues"]))


if __name__ == "__main__":
    main()
