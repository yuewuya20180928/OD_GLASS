#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 03:2x · job fb67af40「ARS45 队列自动派活」
★ISS-307 (hw-lead) 新开并直接派出: ESD 选型轴两路径候选集 (老板 ①② 两个字母的一键化)
=========================================================================================
★**本 job 本轮实测依据 (★自己查盘, 不抄兄弟 job 的报告★)**:
· ★**队列已排空**: `python3 state/advance.py --json` ⇒ `internal: []` (★三个总工名下 open=0 · fixing=0★)
  ⇒ `state/issue_log.yaml` 实读: 302 条里 open=16 (owner 全是 boss/main) · fixing=1 (ISS-131 · owner=main) ★
· ★**子会话全空**: `subagents list` ⇒ active 0 · recent 0 (★hw-lead / sw-lead / mech-lead 都没有在跑的写会话★)
· ★**所以本轮按「开新单」处理 (★队列排空时让内部待办不断线 = 本 job 的存在意义★)**:
  ★**新单的唯一依据 = 机器自己给的派活候选**: `python3 state/gate_check.py` 的【缺口清单】段
  原文写「★**(可直接转成下一轮派活项)**★」⇒ 实测 7 条, 其中 4 条是同一条债:
  ★**hw-lead 的最新一份交卷单缺 [B2] 验收标准自评 / [B3] 证据分级 / [B4] 接口取值声明 / [B5] 未决项与卡点**
  ⇒ ★**Q1 交付齐备率 = 14/18 (★不是假 18/18★)★** ⇒ ★**主因 = main 2026-11-18 03:0x 修了 gate_check 的
  「回退不许掩盖真倒退」** (★`state/gate_check.py` 里新增 `_uses_b_blocks` 判定★) ⇒ 代价是它把真债露出来了 ★
· ★**为什么本轮不只派「补 B 块」这种文档活 (★本单为什么值得一个总工的预算★)**:
  ★**main 03:1x 逐道复扫 10 道闸**: netlist_selfconsistency rc=0 · land_row_anchors rc=0 ·
  onepass_preflight_coverage rc=0 · MECH struct_crosscheck rc=0 · SW demo_panel_spec rc=0 ·
  workpack_state_values rc=0 · onepass_commit_order rc=0 · MECH mech_release rc=0 · bq25896_pinout rc=0
  ⇒ ★**板那一趟的机器前置全清 ⇒ 剩下的红只有两类: ①老板的 4 个字母 ②板那一趟本体 (unc 45→0)★**
  ⇒ ★**但那 4 个字母里有 2 个 (W-2 / W-1b·W-1c) 全落在 ESD 选型轴上 ⇒ 而「选型候选 + 官网证据 + 落位可行性」
  这件事【谁都没交过】⇒ ★**老板现在拍不了这两个字母, 因为他手上没有候选集★** ★
· ★**本单实测出来的地基事实 (★本机 pcbnew / 网表 / 台账 实读, 原样★)**:
  - `D_ESD_USB_D` @ (94.95, 21.80) · 2 焊盘 · Value `ESD 阵列 [待选型] (USB 2.0 双通道)`; `J_USB_C` @ (140.00, 5.25) · 18 焊盘
  - 板框 160×100 (x 0..160 · y 0..100); ★**距 `J_USB_C` 8 mm 内除它自己外没有别的元件** ★
  - 网表: D− 两条网 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 上 ESD 位号数 = **0** ⇒ D− 裸奔 (实测)
  - 网表: `D_ESD_TC` (SP0503BAHT 3 通道 SOT-143) 挂在 VBUS 三张网上 ⇒ **不碰 D+/D−** ⇒ D− 确实没保护
  - 台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` L166 (B-3) 要求 `D_ESD_USB_D` 换 **3 脚封装 (pin1=D+/pin2=D−/pin3=GND)**
  - ★**但同台账 L934 的落表真源型号 = `TPD1E05U06DPYR` = TI 单通道 X1SON-2 (2 脚) ⇒ 台账自己就打架
    ⇒ 这就是「型号轴 (W-1b/W-1c) 必须拍」的实物根据 ⇒ 也是本单第一问 (§2-B1-0)★**
  - 台账 L167 (B-4): 挪到 `J_USB_C` 旁 ≤3.0 mm (现距 47.99 mm) ⇒ 挪位 ⇒ 布线重跑 ⇒ 必须同趟
  - 台账 L168 (B-5): D− 必须补 (理由: Type-C 是 4 条里唯一的「用了就可能坏」)
  - 兄弟单 ISS-306 (sw-lead · 已 verified) 结论: **① W-2 一落 ⇒ R4 两条红自动转绿; 只有老板选「不补」才需另开修闸单**
    ⇒ ★**⇒ 路径乙的「判据口径改法草案」也是本单交卷物 (§2-B3)★** ★
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 板 / 网表 / 脚表 / BOM / 落表台账 / 决策页 / 任何闸脚本 / 任何分片 (hw.yaml 以外) / outbox / 兄弟 job 的任何单
★**纪律**: ISS-307 直接落 fixing (★同一 flock 内原子完成 ⇒ 中间不留 open 窗口 ⇒ 兄弟 job 775d9893 的
advance.py 看不见 ⇒ 不会重复派同一个 agent★) ⇒ ★**幂等: 脚本只在 ISS-307 不存在时才开单★**
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-18"

ISS307_BRIEF_FILE = "state/dispatch_briefs/ISS-307_hw_esd_dual_channel_candidates.md"

ISS307 = {
    "id": "ISS-307",
    "title": (
        "★★[主线内·选型研究类·内部活] ★★【板那一趟的 ESD 选型轴: 老板 ①② 两个字母 (W-2 补不补 D− / "
        "W-1b·W-1c 真 OPN 型号轴) 现在拍不了, 因为没有候选集 ⇒ 本单用【官网】证据把两条路径各交一份候选集 "
        "+ 落位可行性 + 量化代价 ⇒ 让老板只需回【need key + 决策码】就能一次拍完】★★ ⇒ "
        "★**纯分析/选型研究类 · 零写板 · 零落表 · 零改闸 · 零改网表 · 零外发 · 不替老板拍板** ★"
    ),
    "severity": "high",
    "owner": "hw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-18",
    "status": "fixing",
    "external": False,
    "need_keys": ["boss_esd_model_axis_pending_20261117"],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "dispatched_at": TODAY,
    "note": (
        "★**2026-11-18 03:2x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (★status 直接落 fixing ⇒ "
        "兄弟 job 775d9893 的 advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ "
        "★**开单依据 (★main 03:1x 本机实跑, 不抄任何 agent 报告★)** ★ ⇒ "
        "★**① 队列已排空**: `state/advance.py --json` ⇒ `internal: []` (三个总工 open=0 · fixing=0) + "
        "`subagents list` ⇒ active 0 ⇒ ★**所以本轮按「开新单」处理 (队列排空时让内部待办不断线 = 本 job 的存在意义)★** ★ "
        "★**② 派活候选来自机器自己**: `state/gate_check.py`【缺口清单】原文写「★**(可直接转成下一轮派活项)**★」⇒ "
        "实测 7 条 ⇒ 其中 4 条是同一条债 (hw-lead 最新交卷单缺 B2/B3/B4/B5 ⇒ **Q1 = 14/18**) ⇒ "
        "★**成因 = main 03:0x 刚修了 gate_check 的「回退不许掩盖真倒退」(新增 `_uses_b_blocks` 判定) ⇒ 它把真债露出来了★** ★ "
        "★**③ 但本单不只做文档活 (★为什么值得一个总工的预算★)**: main 03:1x 逐道复扫 10 道闸 ⇒ "
        "netlist_selfconsistency / land_row_anchors / onepass_preflight_coverage / MECH struct_crosscheck / "
        "SW demo_panel_spec / workpack_state_values / onepass_commit_order / MECH mech_release / bq25896_pinout 全 rc=0 "
        "⇒ ★**板那一趟的机器前置全清 ⇒ 剩下的红只有两类: ①老板的 4 个字母 ②板那一趟本体 (unc 45→0)★** ⇒ "
        "★**而那 4 个字母里有 2 个 (W-2 / W-1b·W-1c) 全落在 ESD 选型轴上 ⇒ 【选型候选 + 官网证据 + 落位可行性】谁都没交过 "
        "⇒ ⇒ 老板现在拍不了这两个字母, 因为他手上没有候选集 ⇒ 这就是本单存在的理由★** ★ "
        "★**④ 本机实测的地基事实 (★pcbnew / 网表 / 台账 实读★)**: `D_ESD_USB_D` @ (94.95, 21.80) · 2 焊盘 · "
        "Value `ESD 阵列 [待选型] (USB 2.0 双通道)` · `J_USB_C` @ (140.00, 5.25) · 18 焊盘 · 板框 160×100 · "
        "★**距 `J_USB_C` 8 mm 内除它自己外没有别的元件**★ · 网表里 D− 两条网 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) "
        "上的 ESD 位号数 = **0** (D− 裸奔) · `D_ESD_TC` (SP0503BAHT 3 通道 SOT-143) 挂在 VBUS 三张网上 ⇒ **不碰 D+/D−** ★ "
        "★**⑤ 台账内部的硬矛盾 (★本单第一问★)**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` L166 (B-3) 要求 "
        "`D_ESD_USB_D` 换 **3 脚封装 (pin1=D+/pin2=D−/pin3=GND)** ⇒ **一颗双通道件同时吃 D+ 与 D−** ★ "
        "★**但同台账 L934 的落表真源型号 = `TPD1E05U06DPYR` = TI 单通道 X1SON-2 (2 脚) ⇒ 2 脚件物理上接不了 D− "
        "⇒ ⇒ 台账自己打架 ⇒ 这就是「型号轴必须拍」的实物根据★** ★ "
        "★**⑥ 兄弟单 ISS-306 (sw-lead · 已 verified) 的结论被本单直接引用**: ① W-2 一落 ⇒ R4 两条红自动转绿 ⇒ "
        "只有老板选「不补」才需另开一条修闸单 ⇒ ★**⇒ 路径乙的「判据口径改法草案 (★判据不许偷偷放宽★)」也是本单交卷物**★ ★ "
        "★**⑦ 架构轴 ≠ 型号轴**: 老板 2026-11-17 09:49 已拍 A3 架构轴 = V-2 = 1 (2 脚单通道) ⇒ "
        "★**「架构已定」推不出「型号已定」** (★同 ISS-260 的分法★) ★ "
        "★**⑧ 交卷纪律**: 交卷单必须按【标准验收块 B1~B6】写 (★gate_check 的 `REQUIRED_BLOCKS` 口径★) ⇒ "
        "★**Q1 必须 18/18** ★ · ★**加分项**: 可在 `HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md` 文末"
        "【追加】一节标准验收块 (★既有正文一个字不许改★) ⇒ 顺手清掉 Q1 那条口径债 ★ "
        "★**零外发**: 本单不依赖任何外部回复 ⇒ 全部自己网上查 + 标证据等级 + 查不到写降级方案 ★"
    ),
    "task_brief": None,
}


def read(rel):
    with open(os.path.join(PROJ, rel), encoding="utf-8") as f:
        return f.read()


def main() -> int:
    brief = read(ISS307_BRIEF_FILE)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        if "ISS-307" in by_id:
            print("ℹ ISS-307 已存在 ⇒ 幂等跳过 (不重复开单)")
        else:
            ISS307["task_brief"] = brief
            issues.append(ISS307)
            print("✅ ISS-307 新开 (owner=hw-lead · status=fixing ⇒ 直接派出)")

        shutil.copy2(LOG, LOG + ".bak_20261118_0325_cronfb67_open_iss307")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        disp = dl.setdefault("dispatches", [])
        if not any((d or {}).get("issue") == "ISS-307" for d in disp):
            disp.append({
                "issue": "ISS-307",
                "agent": "hw-lead",
                "at": TODAY,
                "brief": (
                    "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 03:2x · ★**新开单 + 直接派出 (status 直接落 fixing ⇒ "
                    "兄弟 job 775d9893 看不见 open 窗口)** ★ · ★**依据 = main 03:1x 本机实跑 (`state/advance.py --json` ⇒ "
                    "internal 排空 + `subagents list` ⇒ active 0 + `state/gate_check.py` 缺口清单原文「可直接转成下一轮派活项」"
                    "+ 10 道闸全绿 + pcbnew/网表/台账 实读)** ★ · ★**brief = `%s` 全文 · 已过命令存在性闸 "
                    "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0** ★" % ISS307_BRIEF_FILE
                ),
                "note": ISS307["note"],
            })
            tmp_dl = DL + ".tmp"
            with open(tmp_dl, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp_dl, DL)
            print("✅ dispatch_log 已写 1 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
