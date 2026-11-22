#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 04:3x · job fb67af40「ARS45 队列自动派活」
★ISS-308 (hw-lead) 新开并直接派出: 「板那一趟 S8 (unconnected 45→0)」的可达性判决书
=========================================================================================
★**本 job 本轮实测依据 (★自己查盘, 不抄兄弟 job 的报告★)**:
· ★**队列已排空**: `python3 state/advance.py --json` ⇒ `internal: []` (三个总工名下 open=0 · fixing=0)
  ⇒ `state/issue_log.yaml` 实读: open=16 (owner 全是 boss=5 / main=11) · fixing=0
· ★**子会话全空**: `subagents list` ⇒ active 0 · recent 0 ⇒ 不是「有在跑的会话所以跳过」, 是真的没活可派
· ★**机器前置全清**: `python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18 · Q7 钉板 md5 闸链 9/9 全绿★)
  ⇒ `python3 state/issue_check.py` ⇒ rc=0 ⇒ 板那一趟开工前机器能挡的都挡住了
  ⇒ 剩下的红只有两类: ①老板的字母 ②S8 本体 (unconnected 45 → 0)
· ★**本轮开单理由 = 「板只改一次」铁律**: S1/S2/S3/S4/S6/S7/S8 必须同趟做完 (INV-1~INV-4)
  ⇒ 如果 S8 能不能做完【现在】没人说得清 ⇒ 这一趟就可能白跑 ⇒ 白跑 = 板 md5 变第二次
  ⇒ ⇒ 交给一个总工的预算, 买【S8 的可达性判决】⇒ 而不是再开一个臂
· ★**本机实测的地基事实 (★pcbnew 读板 / 作业包实读 / 臂总账实读★)**:
  - `bash state/pcbnew_py.sh state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` ⇒ rc=0
    · ★**C4 unconnected items = 45** (★main 04:3x 实跑原样★) · C3 DRC violations = 0 · C7 同点重复过孔 = 0
  - 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17` (⇒ 本单零写板)
  - 作业包 §3-S8 原文: 「45 条里 23 条是高速 DSI/CSI 腿, 全部要跨 SoM 主体 (x 8..76, y 6..56)」
    + 「官方板这 13 条 DSI 腿自己一根都没布通」+ 「其余 22 条死因登记 = ISS-265 §6 的 5 条」
    + 「这是本单唯一一个『可能整趟做完仍然投不了板』的步」
  - `state/UNC_TARGET_MAP.md` §11-11 05:6x: 最佳候选 candidate_v76mx1L_pour (★DRC 0 · unc 26 条 / 22 网名 ·
    名单制闸 rc=0★) 的残余 22 网名清单
  - ★**★本单第一问 = 一个没人写下来过的现象★**: 那 22 条残余里 ★**差分类绝大多数是 N 腿**
    (CSI_D0_CK_N / CSI_D0_D0_N / CSI_D0_D0_N_SRC / CSI_D0_D2_N / CSI_D0_D3_N / DSI_D0_CK_N_SRC /
    DSI_D0_D0_N / DSI_D0_D1_N / DSI_D0_D1_N_SRC / DSI_D0_D3_N …) ⇒ 「P 通 N 不通」是【层分配】症状
    ⇒ 而路由器源码里【正好有】专门治它的 `PCB_PAIR_LAYERSEL` (★env 门控·默认关★)
    ⇒ 而 UNC_TARGET_MAP 原文只写了一句「★`PCB_PAIR_LAYERSEL` 目前无效但无害★」⇒ ★**谁写的 / 哪天的 / 有没有实测支撑 = 未知** ★
  - 臂总账: ★33+ 个臂全部停在 unc 24~29 条 / DRC 0~1 ⇒ 布线参数调优已到平台期
    ⇒ 按 MEMORY 铁律「多个臂在同一批网上失败 ⇒ 先查共享的东西」⇒ 根因在布局/机制, 不在参数
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 板 / 网表 / 脚表 / BOM / 落表台账 / 决策页 / 任何闸脚本 / 任何既有作业包与清单页正文 /
          任何别人的分片 / outbox / 兄弟 job 的任何单
★**纪律**: ISS-308 直接落 fixing (★同一 flock 内原子完成 ⇒ 中间不留 open 窗口 ⇒ 兄弟 job 775d9893 的
advance.py 看不见 ⇒ 不会重复派同一个 agent★) ⇒ ★**幂等: 脚本只在 ISS-308 不存在时才开单★**
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

ISS308_BRIEF_FILE = "state/dispatch_briefs/ISS-308_hw_s8_reachability_verdict.md"

ISS308 = {
    "id": "ISS-308",
    "title": (
        "★★[主线内·分析/作业包类·内部活] ★★【「板那一趟 S8 (unconnected 45 → 0)」的可达性判决书: "
        "残余 22 网名逐条归 5 桶 (老板字母 / GND 卡死 / 差分 N 腿互掐 / 让路闸靶子 / 其它) ⇒ 交出"
        "【老板还差 N 个字母 (N 必须是具体数字)】+【现在就能做的技术活清单】+【S6 落位增补表草案】】★★ ⇒ "
        "★**纯分析/作业包类 · 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板** ★"
    ),
    "severity": "high",
    "owner": "hw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": TODAY,
    "status": "fixing",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "dispatched_at": TODAY,
    "note": (
        "★**2026-11-18 04:3x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (★status 直接落 fixing ⇒ "
        "兄弟 job 775d9893 的 advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ "
        "★**开单依据 (★main 04:2x~04:3x 本机实跑, 不抄任何 agent 报告★)** ★ ⇒ "
        "★**① 队列已排空**: `state/advance.py --json` ⇒ `internal: []` (三个总工 open=0 · fixing=0) + "
        "`subagents list` ⇒ active 0 ⇒ ★**本轮按「开新单」处理 (队列排空时让内部待办不断线 = 本 job 的存在意义)★** ★ "
        "★**② 机器前置全清**: `state/gate_check.py` rc=0 (★Q1 18/18 · Q7 9/9 全绿★) · `state/issue_check.py` rc=0 "
        "⇒ ★**板那一趟开工前机器能挡的都挡住了 ⇒ 剩下的红只有两类: ①老板的字母 ②S8 本体 (unc 45→0)★** ★ "
        "★**③ 本单攻②**: ★**S8 能不能做完, 盘上没有任何一份文档给出答案** ⇒ 而 S8 是 G1 最后一关 ⇒ "
        "★**答错 = 板改第二次 = Gerber/投产包/留证链/盖章/发布全作废** ⇒ ★**这就是本单存在的理由★** ★ "
        "★**④ 本机实测的地基事实 (★原样★)** ★: "
        "· ★**现役板 unc = 45** (`bash state/pcbnew_py.sh state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` "
        "⇒ rc=0 · C3 DRC=0 · C4 unconnected=45 · C7 同点重复过孔=0)★ · 板 md5 611b869e… mtime 2026-11-06 07:07:17 ★ "
        "· 作业包 §3-S8 原文: 「45 条里 23 条是高速 DSI/CSI 腿, 全部要跨 SoM 主体 (x 8..76, y 6..56)」+ "
        "「官方板这 13 条 DSI 腿自己一根都没布通」+ 「其余 22 条死因登记 = ISS-265 §6 的 5 条 (A1/W-1/W-2/W-4/"
        "D_LED_G/FSIN_OUT)」+ 「这是本单唯一一个『可能整趟做完仍然投不了板』的步」★ "
        "· 最佳候选 candidate_v76mx1L_pour (★DRC 0 · unc 26 条 / 22 网名 · 名单制闸 rc=0★) 的残余 22 网名清单 "
        "(★`state/UNC_TARGET_MAP.md` §11-11 05:6x★) ★ "
        "· ★**★本单第一问 = 一个没人写下来过的现象★**: 那 22 条残余里 ★**差分类绝大多数是 N 腿** ⇒ "
        "「P 通 N 不通」是【层分配】症状 ⇒ 而路由器源码里【正好有】专门治它的 `PCB_PAIR_LAYERSEL` (★env 门控★) ⇒ "
        "★**而 UNC_TARGET_MAP 原文只写「目前无效但有害」一句 ⇒ 谁写的/哪天的/有没有实测支撑 = 未知** ★ "
        "· 臂总账: ★33+ 个臂全停在 unc 24~29 / DRC 0~1 ⇒ 参数调优已到平台期 ⇒ ⇒ 根因在布局/机制 ★ "
        "★**⑤ 本单不造活**: sw-lead / mech-lead 名下 open=0 · fixing=0 · 各自的闸全绿 ⇒ 不给他们硬造活 ★ "
        "★**⑥ 交卷纪律**: 交卷单按【标准验收块 B1~B6】写 ⇒ **Q1 必须 18/18** ★ · "
        "★**交卷优先** (★上批子会话 570~1360 s 被父 run 掐·timeout·abortedLastRun=true★) ⇒ 缺口写进 B5 ★ "
        "★**交卷物 3 件 (全部新建)**: `HW/PCB/S8_REACHABILITY_VERDICT.md` · "
        "`HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md` · `state/_iss308_s8_reachability_check.py` ★ "
        "★**零外发**: 本单不依赖任何外部回复 ⇒ 查不到就写 [0数据] + 降级方案 ★"
    ),
    "task_brief": None,
}


def read(rel):
    with open(os.path.join(PROJ, rel), encoding="utf-8") as f:
        return f.read()


def main() -> int:
    brief = read(ISS308_BRIEF_FILE)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        if "ISS-308" in by_id:
            print("ℹ ISS-308 已存在 ⇒ 幂等跳过 (不重复开单)")
        else:
            ISS308["task_brief"] = brief
            issues.append(ISS308)
            print("✅ ISS-308 新开 (owner=hw-lead · status=fixing ⇒ 直接派出)")

        shutil.copy2(LOG, LOG + ".bak_20261118_0430_cronfb67_open_iss308")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        disp = dl.setdefault("dispatches", [])
        if not any((d or {}).get("issue") == "ISS-308" for d in disp):
            disp.append({
                "issue": "ISS-308",
                "agent": "hw-lead",
                "at": TODAY,
                "brief": (
                    "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 04:3x · ★**新开单 + 直接派出 (status 直接落 "
                    "fixing ⇒ 兄弟 job 775d9893 看不见 open 窗口)** ★ · ★**依据 = main 04:2x~04:3x 本机实跑 "
                    "(`state/advance.py --json` ⇒ internal 排空 + `subagents list` ⇒ active 0 + "
                    "`state/gate_check.py` rc=0 (Q1 18/18 · Q7 9/9) + `state/issue_check.py` rc=0 + "
                    "`bash state/pcbnew_py.sh state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` ⇒ "
                    "rc=0 · C4 unconnected = 45 + 作业包 §3-S8 / UNC_TARGET_MAP / 臂总账 实读)** ★ · "
                    "★**brief = `%s` 全文 · 已过命令存在性闸 "
                    "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0** ★" % ISS308_BRIEF_FILE
                ),
                "note": ISS308["note"],
            })
            tmp_dl = DL + ".tmp"
            with open(tmp_dl, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp_dl, DL)
            print("✅ dispatch_log 已写 1 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
