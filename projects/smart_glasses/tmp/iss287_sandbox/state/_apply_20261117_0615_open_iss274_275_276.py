#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_0615_open_iss274_275_276.py
★main (moli) 2026-11-17 06:1x (cron fb67af40 队列自动派活)★
★新开 ISS-274 (hw-lead) + ISS-275 (sw-lead) + ISS-276 (mech-lead) + ISS-273 落 verified★

★★**为什么本轮要自己开单 (★main 本轮 06:1x~06:2x 本机实跑, 不抄任何交卷报告★)** ★★
· ★**`python3 state/advance.py --json` 实测 = `internal[]` = 0 条** ⇒ 根因 = ★**17 条 open 单里 5 条 owner=boss + 12 条 owner=main**
  (★`AGENT_ROLE = {"hw-lead","sw-lead","mech-lead"}` ⇒ owner=main 的单**永远进不了派活队列** ★)
· ★**三个总工本轮全部真空**: `sessions_list` 实测 hw-lead / sw-lead / mech-lead **无 running 会话** ⇒ ★**名额全空** ★
· ★**⇒ 本轮自己挖活开三单 (三个总工各一条, 不撞「一个 agent 同时一个写会话」铁律)★** ★★

★★**本轮挖到的三条活 (★依据全是本机实读, 行号可复核★)** ★★
① ★**ISS-274 (hw-lead) · 板框/坐标系口径收口** ★ — ★**本机实测 (★06:1x~06:2x★)**:
   · 现役板 Edge.Cuts = **160.10 × 100.10mm** / 铜层 **8** / 封装 **186** (★`state/pcbnew_py.sh` 读板★)
   · ★**S6 的 20 个 distinct ref 里, 19 个【已经在目标位】** ⇒ ★**真实位移只有 `R_SEL_D3_P` 一处** (★78.90,9.50 → 122.30,5.50★)
   · ★**作业包 §3-S6 自称「21 个器件 / 21 个坐标」= 重复计数** (`R_SEL_D3_P` 本就在那 10 个 `R_SEL_*` 里) ⇒ 照字面写的机器闸会多算一个不存在的坐标
   · ★**ISS-271 给的两个矩形是 60×30 套A 坐标 ⇒ 搬到现役板会压住 SoM 座**: `D_LED_G` 窗口 (X 33.00..47.71) ⇒ **压 `J_SOM_P3` 的 10 个 DSI 焊盘**;
     检修口开口 (X 47.00..60.00) ⇒ **压 `J_SOM_P1` 的 56 个焊盘** ⇒ ★**ISS-271 交卷单「§5.1 那一句逐字抄进 §3-S6」照字面执行 = 那一趟开工即撞 SoM 座** ★
   · ★**SoM 承载区实测 56.70 × 46.78mm ⇒ 物理上装不进 60×30 / 60×15** ⇒ 「60×30 套A」与现役 demo 板是两种物理产品
· ★**⇒ 这正是「板只改一次」铁律要防的: 那一趟照一份坐标系错乱的作业包开工 ⇒ 板 md5 变第二次 ⇒ 留证链/Gerber/投产包/盖章全白跑** ★

② ★**ISS-275 (sw-lead) · SW 侧 R6 判决源同构收口** ★ — ★**MECH 侧刚在 ISS-273 里把「一落表就红 ⇒ 必人工重锚」切断** (★本机实测: `MECH/check_demo_struct_truth.py` rc=0 23/23 · `--selftest` rc=0 21/21★)
   ⇒ ★**但 SW 侧 R6 现在还判「盘上 md5 == 域侧锚点副本」** (★实读 `SW/tools/check_demo_panel_spec.py:335` 判据 / `:389` 报错★)
   ⇒ ★**ISS-273 交卷单 B5 第 ③ 条原文点名: 「SW 侧同构问题 = main 另派的活, 本单不越界写别人的域」** ⇒ ★**这就是 main 欠的那一派** ★
   ⇒ ★**代价已实测: 锚点已跳 6 跳 (ISS-220→223→233→243→249→257) ⇒ 11-17 05:0x 那一轮白跑了一整轮** ★

③ ★**ISS-276 (mech-lead) · MECH 侧坐标系归一 + 收掉 ISS-273 留下的三条** ★ — ★**本机实测 `state/fragments/mech.yaml`: `iss273_mech_ledger_format_contract` / `iss273_mech_ledger_itself_anchor` 两条 to=main 的 need 仍 pending** ★
   ⇒ ★**且 `state/fragments/pm.yaml` 的 `iss273_h1_anchor_single_source` (★main 自己开的 need★) 实测 pending / answers=0 / foreign=0**
   ⇒ ★**根因: mech-lead 的答案写在 `iss273_mech_judge_source_change` 这个 key 上, 与 main 开的 key 不配对 ⇒ 需求永不闭合** ★
   ⇒ ★**⇒ 本单要【用 main 开的那个原 key】补 answer, 把它闭合** ★

★★**本轮共同边界** ★★
零写板 (★板 md5 `611b869e…` 只许在「板只改一次」那一趟变一次★) · 零落表 · 零改网表/脚表/BOM ·
零改既有判据脚本 · 零开新布线臂 · 不写别人的分片 · 不改 PROJECT_TRACKER.md §0 · 不替老板拍板 · 零外发 (老板 11-12 02:02) ★
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-17"

BRIEF_274 = open(os.path.join(HERE, "dispatch_briefs",
                              "ISS-274_hw_board_frame_coordinate_caliber.md"), encoding="utf-8").read()
BRIEF_275 = open(os.path.join(HERE, "dispatch_briefs",
                              "ISS-275_sw_r6_judgment_source.md"), encoding="utf-8").read()
BRIEF_276 = open(os.path.join(HERE, "dispatch_briefs",
                              "ISS-276_mech_frame_normalize_need_closure.md"), encoding="utf-8").read()


def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {i.get("id"): i for i in issues}

    # ---------- ① ISS-273 落 verified (★verify_by=main, 本轮本机独立复验过★) ----------
    iss273 = by_id.get("ISS-273")
    assert iss273 is not None, "ISS-273 不在 issue_log"
    assert iss273.get("status") == "deferred", \
        "ISS-273 当前 status=%s (预期 deferred) ⇒ 本脚本不该跑" % iss273.get("status")
    iss273["status"] = "verified"
    iss273["verify_result"] = "pass"
    iss273["verify_date"] = TODAY
    iss273["fix_ref"] = ("HANDOFF/2026-11-17_mech-lead_ISS273_锚点台账化.md "
                         "(★B1~B6 + 附A/B/C★) · logs/iss273/acceptance_01_gate.log "
                         "· logs/iss273/acceptance_02_md5_and_gates.log")
    iss273["note"] = (iss273.get("note", "") or "") + (
        "\n\n★**2026-11-17 06:1x (cron fb67af40 队列自动派活) · main 独立复验后落 `verified`** ★\n"
        "★**本轮本机实跑复验 (★不采信交卷报告★)**:\n"
        "· `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0** (★【结论】23/23 组检查通过 | FAIL 0 组★)\n"
        "· `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ **rc=0** (★【反向用例: 21/21 抓到了】★ · R2 绿 / R1·R3·R5a·R5b·R6 红★)\n"
        "· `python3 state/merge.py` ⇒ **rc=0** (★产出 460 · 阻塞 43 · 未闭合需求 265 · 冲突 0★)\n"
        "· `python3 state/gate_check.py` ⇒ **rc=0** (★【Q1 交付齐备率】18/18★)\n"
        "· ★**受保护 5 件 md5 实测逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`\n"
        "  · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607`\n"
        "· ★**门禁脚本本体 md5 = `6972b867c8243bc971408f972dc7727e`** (★与交卷单自述的改后值逐字一致★) ⇒ ★**本轮零写板成立** ★\n"
        "★**deferred 的原因已消失 (★本轮实测: mech-lead 名下无 running 会话 ⇒ 名额已空★)** ⇒ ★**故本单从 `deferred` 落 `verified`** ★\n"
        "★**但机制侧还有尾巴 (★已另派 ISS-276 → mech-lead★)**: ★**`state/fragments/pm.yaml` 的 `iss273_h1_anchor_single_source` 实测仍 pending / answers=0**\n"
        "  ⇒ ★**根因 = mech-lead 的答案写在 `iss273_mech_judge_source_change` 这个 key 上, 与 main 开的 key 不配对 ⇒ 需求永不闭合** ★\n"
        "  ⇒ ★**⇒ ISS-276 要用 main 开的【原 key】补一条 answer 把这条闭合** ★ (★**不写 main 的分片, 用 key 配对来闭合★**)")

    # ---------- ② 新开三条 ----------
    new_items = [
        {
            "id": "ISS-274",
            "title": ("★★[主线内·PCB 线·纯分析+作业包订正类] ★★**「板只改一次」那一趟的【板框/坐标系口径】收口** ★★ "
                      "⇒ 现役板实测 160.10×100.10mm/8层/186封装, 而 MECH 侧两套窗口是 60×30 套A 坐标 "
                      "⇒ ★**搬���现役板会压住 `J_SOM_P3` 的 10 个 DSI 焊盘 / `J_SOM_P1` 的 56 个焊盘** ★ "
                      "⇒ ★**S6 的 20 个 ref 里 19 个已在目标位 (真实位移只有 `R_SEL_D3_P` 一处), 作业包「21 个」是重复计数** ★ "
                      "⇒ ★**照错坐标系开工 = 板 md5 变第二次 = 留证链/Gerber/投产包全白跑** ★"),
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": ("★main 2026-11-17 06:1x~06:2x 本机实读 (★不抄任何交卷报告★) ★\n"
                     "★**① 现役板实测** (`state/pcbnew_py.sh` 读板): Edge.Cuts = **160.10 × 100.10 mm** · 铜层 **8** · 封装 **186**\n"
                     "  · `HW/PCB/demo_mainboard_params.json` 板段 = `160.0/100.0/8层/1.6mm` + `_pending` 自述「先能装下所有件的尺寸」\n"
                     "★**② S6 坐标真值 (★本单最要紧的一条★)**: 读板 21 个 ref 位置 vs `HW/PCB/LAYOUT_FIX_SPEC.md` §3 方案 A 目标 (±0.01mm)\n"
                     "  ⇒ ★**已在目标位 = 19 个** · ★**不同 = 1 个 (`R_SEL_D3_P` 现 78.90,9.50 → 目标 122.30,5.50)** ★\n"
                     "  ⇒ ★**与 §2.2 自述一致: 官方板 8 处交叉全部由 `R_SEL_D3_P` 一条腿造成** ⇒ ★**S6 真实位移只有 1 个器件** ★\n"
                     "  ⇒ 与既有封装重叠 (<1.5mm) = 0 · 落在 160×100 框外 = 0 · 落在 60×30 框外 = **20/21**\n"
                     "★**③ 作业包 §3-S6 的「21 个」是重复计数**: `PCB_PART_POS` 串解析 = **20 个 distinct ref** (无重复)\n"
                     "  ⇒ ★**同一节写「21 个器件 (10×R_SEL_* + 10×TP_DSI_* + R_SEL_D3_P 换位)」⇒ `R_SEL_D3_P` 本就在那 10 个里** ★\n"
                     "  ⇒ ★**后果: 验收判据「① 21 个坐标逐个一致」照字面实现会多算一个不存在的坐标** ★\n"
                     "★**④ ISS-271 的两个矩形是 60×30 套A 坐标, 搬到现役板会撞 SoM 座 (★本机读板实测★)**:\n"
                     "  · `D_LED_G` 首选窗口 X 33.00..47.71 × Y 1.60..28.40 ⇒ **压住 `J_SOM_P3` 的 10 个 DSI 焊盘** (x 34.4/34.8, y 7.96/11.04)\n"
                     "  · 检修口/调试口开口 X 47.00..60.00 × Y 1.665..11.730 ⇒ **压住 `J_SOM_P1` 的 56 个焊盘** (x 47.65..70.35, y 7.61..11.39)\n"
                     "  ⇒ ★**⇒ ISS-271 交卷单 B5 第 ① 条「§5.1 那一句逐字抄进 §3-S6 就行」照字面执行 = 那一趟开工即撞 SoM 座** ★\n"
                     "★**⑤ SoM 承载区实测 56.70 × 46.78mm** (4 个 `J_SOM_P1..P4` 焊盘包络并集) ⇒ **物理上装不进 60×30 / 60×15**\n"
                     "  ⇒ ★**⇒ 「60×30 套A」(SoC 直上板) 与「现役 demo 板」(SoM 承载区) 是两种物理产品 ⇒ 坐标不可互相代入** ★\n"
                     "★**⑥ 三套基线并存**: 现役 160×100/8L/1.6mm/RK3572-SOM · MECH 权威表 60×30/6L/1.0mm/RK3576-SoC\n"
                     "  (★`MECH/BOARD_GEOM_30MM.md` 全文 RK3576 出现 14 次 / RK3572 出现 **0** 次★) · 产品 60×15\n"
                     "★**交付**: ① 新建 `HW/PCB/BOARD_FRAME_CALIBER.md` (板框/坐标系单一权威页) ② 订正作业包 §3-S6 (追加式: 21→20 + 帧声明)\n"
                     "  ③ 订正 `HW/PCB/LAYOUT_FIX_SPEC.md` §3 ④ 新建 `HW/check_board_frame_caliber.py` (C1 帧标签/C2 S6 真值/C3 越界/C4 不压封装/C5 异帧误用/C6 md5 + ≥6 条反向 selftest)\n"
                     "  ⑤ 交卷单 B1~B6 ⑥ 分片 (frag_write.py)\n"
                     "★**类别**: 内部活 · PCB 线 · 纯分析+作业包订正类 · **零写板 · 零落表 · 零改判据阈值** ⇒ **不是老板级拍板** ★"),
            "owner": "hw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": ("2026-11-17 06:1x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮 06:1x~06:2x 本机实跑 + 实读板** ★\n"
                     "⇒ ★**任务书 `state/dispatch_briefs/ISS-274_hw_board_frame_coordinate_caliber.md`** ★\n"
                     "★**hw-lead 名下本轮无 open 队列 (真空; 会话实测无 running) ⇒ 本单是本轮给 hw-lead 的活** ★\n"
                     "★**为什么排第一**: ★**它是「板只改一次」那一趟开工前的【坐标地基】⇒ 地基错了 = 那一趟白做 = 板 md5 变第二次** ★\n"
                     "★**边界**: 零写板 · 零落表 · 零改网表/脚表/BOM · 零改判据脚本 · 零开新布线臂 · 只许新增 HW/ 文件 · 不写 MECH/SW 分片 · 不替老板拍板 P7 · 零外发 ★"),
            "dispatched_at": None,
            "task_brief": BRIEF_274,
        },
        {
            "id": "ISS-275",
            "title": ("★★[主线内·SW 侧·门禁机制类] ★★**SW 侧 R6 判决源同构收口 (镜像 MECH 侧 ISS-273 已证机制)** ★★ "
                      "⇒ ★**R6 现在仍判「盘上 md5 == 域侧锚点副本」⇒ 上游每合法落一次表 = 域侧副本当场过期 = 门禁红 = 再开一条人工重锚单** ★ "
                      "⇒ ★**锚点已跳 6 跳 (ISS-220→223→233→243→249→257) ⇒ 11-17 05:0x 那一轮白跑了一整轮** ★ "
                      "⇒ ★**合法落表不再红, 而「悄悄换真源」仍然红** ★"),
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": ("★main 2026-11-17 06:1x 本机实读 (★不抄任何交卷报告★) ★\n"
                     "★**① 病灶 (★实读行号★)**: `SW/tools/check_demo_panel_spec.py`\n"
                     "  · `:335` 判据原文「① 盘上真源的 md5 == 锚点 §1 `entries[].md5`」\n"
                     "  · `:389` 报错原文「R6 盘上真源 md5 %s = %s ≠ 锚点登记 %s (真源被换了或锚点过期)」\n"
                     "  · `:129` 锚点位置 `LEDGER_DOC = SW/SW_MD5_BASELINE_LEDGER.md`\n"
                     "  ⇒ ★**判决源 = 域侧锚点副本 (SW 自己抄的一份 md5) ⇒ 上游每合法落一次表就当场过期 ⇒ 必人工重锚** ★\n"
                     "★**② 代价已跑过 6 跳**: `state/fragments/hw.yaml` 的 `source_ledger` = ISS-220 → 223 → 233 → 243 → 249 → 257\n"
                     "  ⇒ ★**每跳 = 上游一次合法落表 = 再开一条 dispatch 单人工重锚** ★\n"
                     "  ⇒ ★**实测代价: 2026-11-17 05:0x 那一轮白跑了一整轮 (派了 ISS-253, 而那单 11-16 20:0x 就 verified 且已被 ISS-259 第 6 跳覆盖; 派单还写错了文件)** ★\n"
                     "★**③ MECH 侧刚把同一个病治好了 (★你照抄的对象★)**: `MECH/check_demo_struct_truth.py`\n"
                     "  · `:325` `ledger_records()` (★从台账抽该文件的落表记录 ⇒ [{prev,new,iss,sec,row}] · 行序无关★)\n"
                     "  · `:353` `ledger_state()` (★算链头/链/产出单号表 · 取不准 ⇒ head=None ⇒ 判红★)\n"
                     "  · ★**语义: 盘上 md5 ↔ 台账链头 ⇒ 合法落表不再红 (链头自动前移) · 悄悄换真源照样红 · 判最新靠有向链不靠行序 ⇒ 取错只会假红** ★\n"
                     "  ⇒ ★**本机实测 MECH 侧现状: `MECH/check_demo_struct_truth.py` rc=0 (23/23) · `--selftest` rc=0 (21/21)** ⇒ ★**机制已证, 你是镜像不是探索** ★\n"
                     "★**④ 判决源要读的台账现值**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.5/§18.4 = 「单号 | 文件 | 旧 md5 | 新 md5 | 变了?」四项同行\n"
                     "  ⇒ 现值: 网表链头 `e06c1dd6…` (by ISS-257) · 脚表链头 `287e7861…` (by ISS-257)\n"
                     "★**⑤ 这是 main 欠的那一派 (★ISS-273 交卷单 B5 第 ③ 条原文★)**:\n"
                     "  「★**SW 侧同构问题** (`SW/tools/check_demo_panel_spec.py` 的 R6 = 同一个「一落表就红」机制) ★**是 main 另派的活, 本单不越界写别人的域**★」\n"
                     "★**交付**: ① 改 `SW/tools/check_demo_panel_spec.py` 的 R6 (判决源 → 台账链头; 域侧副本降级为历史留痕; 取不准一律判红)\n"
                     "  ② 追加 `SW/SW_MD5_BASELINE_LEDGER.md` §1 角色声明 + §3 留痕 ③ 新建 `SW/tools/check_demo_panel_spec_r6_selftest.py` (R1 红/R2 绿/R3 红/R4 绿/R5a 红/R5b 红/R6 红)\n"
                     "  ④ 交卷单 B1~B6 ⑤ 分片 (frag_write.py) + 1 条 need 给 main (★落表台账格式契约★)\n"
                     "★**类别**: 内部活 · SW 侧 · 门禁机制类 · **零写板 · 零落表 · 零改网表/脚表/BOM · 零改判据阈值** ⇒ **不是老板级拍板** ★"),
            "owner": "sw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": ("2026-11-17 06:1x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮 06:1x 本机实读 + ISS-273 交卷单 B5 第 ③ 条原文** ★\n"
                     "⇒ ★**任务书 `state/dispatch_briefs/ISS-275_sw_r6_judgment_source.md`** ★\n"
                     "★**sw-lead 名下本轮无 open 队列 (真空; 会话实测无 running) ⇒ 本单是本轮给 sw-lead 的活** ★\n"
                     "★**边界**: 零写板 · 零落表 · 零改网表/脚表/BOM · 只许改 R6 那一段 + 新增 helper 段 · R1~R5/R7 一字不许动 · 域侧副本 6 跳历史一条不许删 · 零外发 ★"),
            "dispatched_at": None,
            "task_brief": BRIEF_275,
        },
        {
            "id": "ISS-276",
            "title": ("★★[主线内·MECH 侧·纯分析+规格页订正类] ★★**「板只改一次」那一趟的 MECH 侧【坐标系归一 + 收掉 ISS-273 留下的三条】** ★★ "
                      "⇒ ★**ISS-271/267 的两个窗口是 60×30 套A 坐标 ⇒ 搬到现役 160×100 台架板会压住 SoM 座 (`J_SOM_P3` 10 焊盘 / `J_SOM_P1` 56 焊盘)** ★ "
                      "⇒ ★**另: main 开的 need `iss273_h1_anchor_single_source` 实测仍 pending (答案 key 不配对 ⇒ 永不闭合)** ★"),
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": ("★main 2026-11-17 06:1x 本机实读 (★不抄任何交卷报告★) ★\n"
                     "★**① 坐标帧冲突 (★实测★)**: ISS-271 交卷单 B5 第 ① 条原文「§5.1 那一句逐字抄进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6 就行」\n"
                     "  ⇒ ★**照字面执行 = 那一趟开工即撞 SoM 座** ★:\n"
                     "  · `D_LED_G` 首选窗口 X 33.00..47.71 × Y 1.60..28.40 ⇒ **压住 `J_SOM_P3` 的 10 个 DSI 焊盘**\n"
                     "  · 检修口/调试口开口 X 47.00..60.00 × Y 1.665..11.730 ⇒ **压住 `J_SOM_P1` 的 56 个焊盘**\n"
                     "  ⇒ ★**这两组数在 60×30 板上是对的, 在现役 160×100 板上是错的** ★\n"
                     "★**② 现役板 SoM 承载区实测 56.70 × 46.78mm ⇒ 装不进 60×30 / 60×15 ⇒ 两块板是两种物理产品, 坐标不可互相代入** ★\n"
                     "★**③ 现役板实际位置 (★你归一化的输入★)**: `J_DEBUG`@(144.30,58.00) 4 焊盘 · `J_UART`@(20.74,70.00) 2 焊盘\n"
                     "  ⇒ ★**相距 123.6mm (⇒ 你 §4 说的「开口 X 49.21..59.41 在盘上板不成立」实测成立)** ★\n"
                     "  · `D_LED_G`@(101.25,56.80) ↔ `R_LED_G`@(5.90,62.50) ⇒ ★**`LED_G_D` 走线 93.49mm 的两端 (你 05:1x 实算 93.492727 对得上)** ★\n"
                     "★**④ 三条待答 need (★本机实读 `state/fragments/mech.yaml`★)**:\n"
                     "  · `iss273_mech_ledger_format_contract` → main ⇒ **pending**\n"
                     "  · `iss273_mech_ledger_itself_anchor` → main ⇒ **pending**\n"
                     "  · ★**`state/fragments/pm.yaml` 的 `iss273_h1_anchor_single_source` (★main 自己开的 need★) ⇒ pending / answers=0 / foreign=0** ★\n"
                     "    ⇒ ★**根因 = 你的答案写在 `iss273_mech_judge_source_change` 这个 key 上 ⇒ 与 main 开的 key 不配对 ⇒ 需求永不闭合** ★\n"
                     "    ⇒ ★**⇒ 本单要【用 main 开的原 key `iss273_h1_anchor_single_source`】补一条 answer, 把它闭合** ★\n"
                     "★**⑤ 落表台账格式契约现值**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.5/§18.4 = 「单号 | 文件 | 旧 md5 | 新 md5 | 变了?」四项同行\n"
                     "  ⇒ ★**这就是 MECH 侧 `ledger_records()` 靠它抽链的格式 ⇒ 契约现值 = 这四项同行** ★\n"
                     "★**交付**: ① 新建 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (坐标系归一页) ② 追加式订正 `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md`\n"
                     "  ③ 新建 `MECH/check_board_frame_coords.py` (C1 帧标签/C2 归一后窗口不压 SoM 座/C3 负向断言/C4 md5 + ≥5 条反向 selftest)\n"
                     "  ④ 用原 key 补 answer 闭合 pm.yaml 那条 + 答另两条 need ⑤ 交卷单 B1~B6 ⑥ 分片 (frag_write.py)\n"
                     "★**类别**: 内部活 · MECH 侧 · 纯分析+规格页订正类 · **零写板 · 零落表 · 零改既有 MECH 判据脚本** ⇒ **不是老板级拍板** ★"),
            "owner": "mech-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": ("2026-11-17 06:1x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮 06:1x 本机实读板 + 实读 fragments★ ★\n"
                     "⇒ ★**任务书 `state/dispatch_briefs/ISS-276_mech_frame_normalize_need_closure.md`** ★\n"
                     "★**mech-lead 名下本轮无 open 队列 (真空; 会话实测无 running) ⇒ 本单是本轮给 mech-lead 的活** ★\n"
                     "★**与 ISS-274 (hw-lead) 的分界**: ★**274 = PCB 侧的板框/坐标帧权威页 (HW/ 域) · 276 = MECH 侧的口径归一 + need 收口 (MECH/ 域) ★\n"
                     "  ⇒ ★**两边都不许改对方的文件** ★\n"
                     "★**边界**: 零写板 · 零落表 · 零改既有 MECH 判据脚本 (check_demo_struct_truth.py 6972b867… 一字不许动) · 零改 HW/ · 只写自己分片 · 零外发 ★"),
            "dispatched_at": None,
            "task_brief": BRIEF_276,
        },
    ]

    for it in new_items:
        assert it["id"] not in by_id, "%s 已存在" % it["id"]
        issues.append(it)

    bak = os.path.join(HERE, "issue_log.yaml.bak_20261117_0615_open274_275_276")
    shutil.copy2(LOG, bak)
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))

    for iid, brief in (("iss274", BRIEF_274), ("iss275", BRIEF_275), ("iss276", BRIEF_276)):
        atomic_write(os.path.join(HERE, "tasks", "advance_%s.md" % iid), brief)

    print("✅ ISS-273 落 verified (verify_by=main, verify_date=%s)" % TODAY)
    print("✅ 新开 3 条 (status=open): ISS-274 (hw-lead) / ISS-275 (sw-lead) / ISS-276 (mech-lead)")
    print("   备份: %s" % bak)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
