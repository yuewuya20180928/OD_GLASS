#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20260723_1400_cron775d_open_iss361_362.py —— main 开 ISS-361 (hw-lead) + ISS-362 (sw-lead)

★本单只做 1 件 (★不动板·不改网表真源·不外发·不替老板拍板·不改别人分片★):
  ① 开 ISS-361 (owner=hw-lead, status=open) —— 任务书 = state/dispatch_briefs/ISS-361_hw_fp_truth_coverage_gap.md
  ② 开 ISS-362 (owner=sw-lead, status=open) —— 任务书 = state/dispatch_briefs/ISS-362_sw_fp_truth_impact.md
  ③ 零 churn 落盘 (★append-only·历史字节一字不动★)

★为什么开这两单 (★事实全部本机实读, 不抄任何 agent 报告★):
  · advance.py --json ⇒ internal=[] (三个总工名下 open 全为 0 ⇒ 队列真空)
  · 但本机实读发现【板那一趟】的真源侧有两处【没有任何闸覆盖】的缺口:
    ① ISS-356 的封装真值基线口径 = 必装 ∩ 非NET/TP ∩ footprint=='待定' ⇒ 实测 100 件 (78+22)
       ⇒ 而板上占位脚号器件 C4 = 158 件 ⇒ 两集合只交 77 ⇒ 差集 81 件 = TP 42 + DNP 26 + 13 真器件
       ⇒ 那 13 件的 BOM footprint 栏是描述串 (★不是 '待定'★) ⇒ 被 ISS-356 那一个条件挡在门外
       ⇒ 其中 12 件在 FP_TRUTH_BASELINE.md 里【没有目标 lib:name】⇒ 且 9 件正是那一趟的 P0 改项
       ⇒ 而 state/board_trip_baseline_20260723.txt 的 C4 判据写的是「158 全部收敛」⇒ 【不可能满足】
    ② SW 侧对【S10 换封装】这一跳零准备: ISS-321/323/327 三单只覆盖了 S1 改名; SW 全域读 footprint 栏 0 处;
       SW 侧 8 条待办 need 引的 md5 逐条实测全部是陈旧值 (★链头早已前移到 ISS-302★)
  ⇒ 两单都是【纯分析 / 作业包 / 机器闸类·零写板】⇒ 符合「板只改一次 ⇒ 先派纯分析类」纪律
"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

B361 = open(os.path.join(PROJ, "state/dispatch_briefs/ISS-361_hw_fp_truth_coverage_gap.md"),
            encoding="utf-8").read()
B362 = open(os.path.join(PROJ, "state/dispatch_briefs/ISS-362_sw_fp_truth_impact.md"),
            encoding="utf-8").read()

T361 = (
    "★★[★新主线·PCB 线·「板那一趟」封装真值覆盖缺口·纯分析+文档+机器闸·零写板] ★★【ISS-356 交卷的「封装真值基线」只覆盖 "
    "「必装 ∩ 非 NET/TP ∩ footprint 栏=='待定'」这个口径 ⇒ 实测 78(镜脚主PCB) + 22(镜框充电板) = 100 件; 但「板那一趟」真正要收口的是"
    "「板上 158 个占位脚号器件」⇒ 两集合只交 77 ⇒ 差集 81 件 = TP_* 42 + DNP 26 + ★★13 件【真器件·必装·非 TP】★★ ⇒ 那 13 件的 BOM "
    "footprint 栏写的是描述串 (例 `Q_AND` = `★板文件封装: 3 焊盘 ([待选型] N-MOS (硬件 AND))`) ⇒ 被 ISS-356 那【一个条件】挡在门外 ⇒ "
    "其中 12 件在 `HW/FP_TRUTH_BASELINE.md` 里【没有目标 lib:name】⇒ 且 9 件正是那一趟的 P0 改项 (Q_AND/Q_PG/Q_ENVC 的 D/S/G vs G/S/D 脚序 · "
    "D_ESD_CAM 脚序反 · D_ESD_USB_D 2→3 脚 · 5 件按键 land 外扩) ⇒ ★★而 `state/board_trip_baseline_20260723.txt` 的 C4 判据写的是「158 全部"
    "收敛」⇒ 用 ISS-356 的基线【永远凑不齐】⇒ 那条判据目前【不可能满足】而没有任何闸会发现 ⇒ ⇒ 那一趟照现状开工会带着 81 件未收敛的"
    "占位脚号出板 ⇒ 【改了板却没改封装】⇒ 改完还是错的 ⇒ 板 md5 第二次变】★★ ★**本单只出【一页 + 一条机器闸】, 把这条判据从【一句话】变成"
    "【可数·可点名·可机器判】(★四桶目标值: TP 42 / DNP 26 / 靶内 77 / 缺口 13★)· 零写板·零落表·零外发·不代老板拍板**★"
)

D361 = (
    "★**main 2026-11-23 13:5x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**① 三个口径的实跑读数**: "
    "`python3 HW/check_fp_truth_baseline.py` ⇒ C0~C6 全 PASS · 事实「靶子(镜脚主PCB)=78 靶子(镜框充电板)=22 合计=100」★ · "
    "`bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ 「C4 焊盘号为占位(行序)的器件 158 个」★ · "
    "★**② main 本机实算的集合关系**: C4-158 ∩ ISS-356-100 = ★**77**★ · C4-158 − ISS-356-100 = ★**81**★ ⇒ "
    "81 件成分 = TP_* 42 (被 `type=='TP'` 排除) + DNP 26 (被 `dnp=='DNP'` 排除) + ★**13 件真器件必装非 TP**★ ★ "
    "★**③ 那 13 件为什么被挡在门外 (★根因·不是遗漏★)**: 它们的 BOM `footprint` 栏是描述串 (★`★板文件封装: N 焊盘 (…)`★) "
    "而不是字面量 `待定` ⇒ ISS-356 的判据 `footprint=='待定'` 一个条件就全挡掉 ⇒ ★**13 件 = CHG_GND_STAR / D_ESD_CAM / D_ESD_DEMO / "
    "D_ESD_USB_D / FB_DEMO / Q_AND / Q_ENVC / Q_PG / SW_BOOT / SW_KEY_PWR / SW_KEY_VM / SW_KEY_VP / SW_RST**★ ★ "
    "★**④ 页内覆盖**: 13 件里只有 CHG_GND_STAR 有目标 lib:name (§2.2 靶外同族 `TestPoint:TestPoint_Pad_D1.0mm`) ⇒ **12 件没有** ★ "
    "★**⑤ 板面真状态**: 186 个封装 · `GetFPIDAsString()` 唯一值 = `''` ⇒ 板是自绘通用占位 ⇒ 不是「库名写错」★ "
    "★**⑥ 脚数≥3 的 (脚号顺序真会出事的)**: Q_AND (3) / Q_ENVC (3) / Q_PG (3) / X1 (3·DNP) ⇒ 前 3 件正是 B10/B11/B12 三条 P0 land 改项★ "
    "★**⑦ 与 ISS-354 的关系**: ISS-354 §V-3 的 5 个 ref (Q1/Q2/U_BATPROT/U_LDO_S28/U_SUPV) 全 dnp=DNP 且全不在 C4-158 ⇒ "
    "**ISS-354 与 ISS-356 两套名单零重叠·两套都不覆盖这 13 件** ★ "
    "★**⑧ 现有闸覆盖**: `state/check_pcb_nets.py` 里 `footprint` 命中 0 次; `HW/check_netlist_selfconsistency.py` 只查个别 ref 的板面属性 "
    "(d3_board_value / d4_esd_pads / d4_esd_pad1_net …) ⇒ **那 13 件没有任何一件被现有闸覆盖** ★ "
    "★**⑨ 边界**: 零写板 (md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:53:30` 前后双证) · 零落表 · 零改既有闸 · "
    "零改既有页面正文 (`HW/FP_TRUTH_BASELINE.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / "
    "`state/board_trip_baseline_20260723.txt` 老字一字不删·只在交卷页写建议) · 零外发 · 零采购 · 不代老板拍 (D_ESD_USB_D 2→3 脚是老板 W-1/W-2) · "
    "只写 `state/fragments/hw.yaml` (走 frag_write.py · 写前后记 md5 基线·被并发改过就停) · 不改 PROJECT_TRACKER.md §0 · "
    "★沙盒落项目盘 `tmp/` (本机 /tmp 配额已满) · 单条 exec ≤ ~120 秒 ★"
)

N361 = (
    "★★2026-11-23 14:0x · cron 775d9893 (ARS45 继续执行后继计划) 开单 (★项目总工 main★) ★★ ★**开单依据**: ① `state/advance.py --json` ⇒ "
    "internal=[] ⇒ 三个总工名下 open 全为 0 ⇒ 队列真空 ⇒ 但本机实读发现【板那一趟】真源侧有【两处没有任何闸覆盖】的缺口 ⇒ "
    "**这 13 件缺口 = 那 158 条判据凑不齐的直接原因** ⇒ 照现状开工 ⇒ 改了板却没改封装 ⇒ 板 md5 第二次变 ★★ "
    "★**判定**: 纯分析 + 文档 + 机器闸类 · 零写板 · 零落表 · 零外发 · 零新增拍板项 · ★**派活时刻 2026-11-23 14:0x · status 落 fixing ⇒ "
    "下一轮 advance.py 的 in_flight 规则看不见本单 ⇒ 不会重复派** ★ ★**不占老板拍板面** ★"
)

T362 = (
    "★★[★新主线·PCB 线·SW 侧「S10 换封装真值」那一跳的影响面·纯分析+沙盒预演+机器闸·零写板] ★★【「板只改一次」那一趟 (S1~S13) 会"
    "【合法地】把三份真源 (网表/脚表/BOM) 的 md5 一起换掉; SW 侧 7 道闸 + 1 道准出汇总闸 + 8 条板侧输入清单全部盯着这些真源; 但【S10 换"
    "封装真值】这一跳与【S1 改名】那一跳【换的东西根本不是一类】⇒ 而 SW 侧现在【没有任何一份文件】说明这一跳会发生什么 ⇒ 且 SW 侧还挂着 "
    "8 条引着【过期 md5】的待办重锚 need ⇒ ★★⇒ 本单 = 把「S10 换封装」这一跳对 SW 侧的全部影响做成【一页 + 一道沙盒预演闸】, 让那一趟当天 "
    "SW 侧【红的每一条都能被解释】而不是【现场抓瞎】⇒ 最坏的结果是有人为「让闸变绿」去改真源/改锚点/放宽判据 ⇒ 那正是 ISS-273/275/284 "
    "三单花大力气堵掉的「悄悄换真源」漏洞】★★ ★**本单【不许】往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条 (★那是改那一趟的清单·归 main 裁★) · "
    "零写板·零落表·零改既有闸·零改锚点 md5·零外发·不代拍**★"
)

D362 = (
    "★**main 2026-11-23 13:5x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**① 这一跳是什么 (★ISS-356 交卷页逐字★)**: 「本单不落表: 真值要落到"
    "原理图 `Footprint` 属性 / BOM `footprint` 栏 / 板生成器, 那是『板那一趟』的活」⇒ 那 78+22 件的 footprint 栏会变成真库封装名 ⇒ "
    "★**三份真源都带 footprint 栏** (netlist_v1.csv 第 14 栏 / netlist_v1_pins.csv 第 12 栏 / BOM_v1.csv 第 10 栏) ⇒ ★**这一跳必然换 3 个 md5** ★ "
    "★**② SW 侧 10 道闸基线逐道实跑 rc 全 0** (check_onepass_sw_sync / check_sw_ref_reachability / check_landing_trace_obligation / "
    "check_demo_panel_spec / 三道 r6 selftest / check_shutdown_semantics / check_timing_review_adc_sync / timing_check) + "
    "check_onepass_sw_release rc=0 且 `--selftest` 末行「✅ 一致」★ "
    "★**③ S1 那条线 SW 侧有准备, S10 这条线零准备 (★关键事实★)**: ISS-321/323/327 三单全 verified 且覆盖 S1 改名; 但 "
    "`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` 全文 footprint 命中 = 1 · `HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md` "
    "全文 footprint 命中 = 1 · `SW/tools/check_onepass_sw_sync.py` 全文 footprint 命中 = **0** ⇒ ★**SW 全域没有任何一道闸读 footprint 栏** ★ "
    "★**④ 8 条板侧输入清单里没有 footprint 这一维**: SW01~SW08 归属步 S2/S4/S8/S9/S10 ⇒ 6 条 current_state 嵌着会改名的位号 "
    "(SW_BOOT/SW_KEY_PWR/SW_KEY_VM/SW_KEY_VP/SW_RST/D_CHG_LED/D_LED_G/D_LED_R/TP_INT/C_VBUS_GND/D_ESD_USB_D) ⇒ 那是 ISS-323 第 3 件要处理的 "
    "「三条现状探针改成从网表实读」⇒ ★**S1 有准备·S10 连登记都没有** ★ "
    "★**⑤ 台账锚点落后 6 跳 + 8 条 need 引的全是陈旧值**: `SW/SW_MD5_BASELINE_LEDGER.md` 的 source_ledger.entries[] 只有 2 条 (ISS-257 那跳) ⇒ "
    "登记值 `e06c1dd6…`/`287e7861…` vs 盘上现值 `6aee500e…`/`9174309d…`; 而 main 实跑 `sw_ledger_state()` 对判决源台账 "
    "`HW/SCHEMATIC_LANDING_V1_LANDED.md` ⇒ 三件链头全对 (ISS-302) ⇒ ★**闸的判决源是台账链头不是域侧副本 ⇒ 它今天 rc=0 是设计不是侥幸** ★ "
    "★**⑥ 但 STATE.yaml 里 to=sw-lead 的 8 条待办 need (iss233_sw_md5_reanchor / iss236_h1_reanchor / iss239_h1_reanchor_sw / "
    "iss249_h1_reanchor_netlist_md5_sw / iss257_h1_reanchor_to_sw_lead / iss260_h1_reanchor_after_v2_land / iss236_h1_reanchor_v2 / "
    "iss283_sw_anchor_reanchor_after_landing) 里引的 32 位 md5, main 逐条比对盘上现值+台账链头 ⇒ 一条都不等 ⇒ 全是陈旧值** ★ "
    "且它们各自的触发单 (ISS-233/236/249/257/260/283) 已全部 verified ⇒ ★**这 8 条是【已过期但还挂在未闭合队列里】的·既虚增未闭合数·又若被误当成"
    "「待执行的重锚指令」照抄 md5 就会把锚点写错** ★ "
    "★**⑦ 边界**: 零写板 (md5 `611b869e13518c3c023fb178f91a0075` 前后双证) · 零落表 · 零改既有闸 (含 check_onepass_sw_sync.py / "
    "check_onepass_sw_release.py / check_demo_panel_spec.py) · 零改 `SW/BOARD_ONEPASS_SW_SYNC.md` (★不许加第 9 条★) · "
    "零改 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块 · ★**零改台账锚点 md5 (「手改 md5 凑绿」是 ISS-275/284 堵死的路·本单绝对不许走)** ★ · "
    "零外发 · 不代老板拍 · 只写 `state/fragments/sw.yaml` (走 frag_write.py · 写前后记 md5 基线) · 不改 PROJECT_TRACKER.md §0 · "
    "★沙盒落项目盘 `tmp/` + TMPDIR 指项目内 (本机 /tmp 配额已满) + ★★禁止 `os.symlink()` (★ISS-327 cont1 写穿真件的根因★)★★ ★"
)

N362 = (
    "★★2026-11-23 14:0x · cron 775d9893 (ARS45 继续执行后继计划) 开单 (★项目总工 main★) ★★ ★**开单依据**: ① `state/advance.py --json` ⇒ "
    "internal=[] (三个总工名下 open 全为 0 ⇒ 队列真空) ② main 本机实读发现【板那一趟】在 SW 侧有一条【零准备】的跳 (S10 换封装真值 ⇒ 三份真源 md5 "
    "同时换) ⇒ 而 S1 那条线 SW 侧有 ISS-321/323/327 三单准备 ⇒ 两跳不同类却只准备了一条 ⇒ ③ SW 侧还挂着 8 条引着陈旧 md5 的待办重锚 need "
    "(实测 8 条 need 的 md5 与盘上现值+台账链头逐条比对 ⇒ 一条都不等) ⇒ ④⇒ **这一跳当天若红了, SW 侧没有任何一份文件能解释「预期 vs 坏了」** ⇒ "
    "最坏结果是有人为让闸变绿去改真源/改锚点/放宽判据 ★ ★**判定**: 纯分析 + 沙盒预演 + 新建只读闸类 · 零写板 · 零落表 · 零外发 · "
    "零新增拍板项 · ★**派活时刻 2026-11-23 14:0x · status 落 fixing ⇒ 下一轮 advance.py 的 in_flight 规则看不见本单 ⇒ 不会重复派** ★ "
    "★**不占老板拍板面** ★"
)

ENTRIES = [
    {"id": "ISS-361", "title": T361, "severity": "high", "source_blocker": "ISS-356",
     "source_agent": "main", "desc": D361, "owner": "hw-lead", "reporter": "main",
     "raised": "2026-11-23", "due": "2026-11-25", "status": "open", "external": "false",
     "task_brief": B361, "dispatched_at": None, "verify_by": "main", "verify_result": None, "note": N361},
    {"id": "ISS-362", "title": T362, "severity": "high", "source_blocker": "ISS-356",
     "source_agent": "main", "desc": D362, "owner": "sw-lead", "reporter": "main",
     "raised": "2026-11-23", "due": "2026-11-25", "status": "open", "external": "false",
     "task_brief": B362, "dispatched_at": None, "verify_by": "main", "verify_result": None, "note": N362},
]


def main():
    src = open(LOG, encoding="utf-8").read()
    chunk = yaml.safe_dump(ENTRIES, allow_unicode=True, sort_keys=False, width=200)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    shutil.copy2(LOG, LOG + ".bak_%s_cron775d_open_iss361_362" % STAMP)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src + chunk)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)
    ids = [i.get("id") for i in items]
    print("台账条数 = %d · ISS-361 在盘 = %s · ISS-362 在盘 = %s · 零重复 id = %s"
          % (len(ids), "ISS-361" in ids, "ISS-362" in ids, len(ids) == len(set(ids))))
    for i in items:
        if i.get("id") in ("ISS-361", "ISS-362"):
            print("  %s status=%s owner=%s brief=%d B" % (i.get("id"), i.get("status"),
                                                         i.get("owner"), len(i.get("task_brief") or "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
