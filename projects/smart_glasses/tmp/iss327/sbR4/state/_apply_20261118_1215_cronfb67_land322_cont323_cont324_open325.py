#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-322 落地 (fixing → verified) + ISS-323/ISS-324 续做 brief 追加 + 新开 ISS-325 (hw-lead)
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 12:1x ★

★**为什么有本脚本** (★main 12:1x 本机实读·不抄 agent 报告★):
  · ISS-322 (hw-lead) 子会话 `agent:hw-lead:subagent:b3cb742d-…` 11:08 起 · **11:41:46 跑完 (status=done)**
    ⇒ main 12:1x 独立复核:
      - 交付页 `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` = 64,052 B · **544 行** · §0~§7 七节全在 · 占位符 0
      - 交卷页 `HANDOFF/2026-11-18_hw-lead_ISS322_S8布线归零作业包.md` = 27,804 B · **254 行** · B0~B6 齐全 · 占位符 0
      - `logs/iss322/` = **31 件** (30 份 raw + `scripts/` 10 个只读探针)
      - **悬空引用 = 0** (main 实测: 交付页引 21 个 logs 路径 + 交卷页引 27 个 ⇒ 全部存在)
      - 分片 `state/fragments/hw.yaml` 命中 `iss322|ISS-322` = **35** (已写) · needs `iss322_s8_*` = **7** 条
      - ★零写板双证: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未变
      - ★闸链本机实跑: `state/gate_check.py` ⇒ **rc=0** · Q1 **18/18** · Q7 钉板 md5 闸链 **9/9 全绿**
                     `state/merge.py` ⇒ rc=0 (产出 655 · 阻塞 43 · 未闭合需求 330 · 冲突 0)
                     `state/issue_check.py` ⇒ rc=0 · `state/compare_arm_official.py --self-test` ⇒ ALL TESTS PASS
    ⇒ 交卷判据 (交卷页 B0~B6 + 交付页 §0~§7 + 分片已写 + 零写板 + 闸链全绿) 五件齐 ⇒ 落 verified

  · ISS-323 (sw-lead) 子会话 `agent:sw-lead:subagent:fc903f9a-…` 11:46 起 · **12:0x 被父 cron run 连带 abort**
    (★`status=timeout` · `abortedLastRun=true` · runtimeMs=1438900★)
    ⇒ main 12:1x 实读: ★**交付物 ①②③ 全在盘 (主文档 73,571 B · 交卷页 32,099 B · logs 106 件)· 但
    `state/fragments/sw.yaml` mtime = 11:12:06 (★早于本单开工 ⇒ 一字未写★) ⇒ 只差【写分片 + 1 处乱码 + 重跑闸链】**
    ⇒ **status 保持 fixing** (★不回滚成 open ⇒ 下一轮 cron 的 in_flight 规则会跳过 sw-lead ⇒ 无重复派活窗口★) ⇒ **追加 cont1 brief**

  · ISS-324 (mech-lead) 子会话 `agent:mech-lead:subagent:ed19e10c-…` 11:46 起 · **12:0x 同样被父 run 连带 abort**
    ⇒ main 12:1x 实读: ★**读数全在 `logs/iss324/` (20 件·含候选终表 C1~C6)· 但交付物 ①② + 分片【一个都不在盘上】**
    ⇒ **status 保持 fixing** ⇒ **追加 cont1 brief**

★**为什么新开 ISS-325 而不是复用**: ISS-322 的 need `iss322_s8_rsel_lane_order` (老板 G7) 的唯一验证手段 = ★**把
  「左上布局」第一次真跑一遍**★ ⇒ ★**main 12:1x 查遍 53 个臂脚本: 没有任何一个把 `TP_DSI_*` 钉到左上** ⇒
  ⇒ ISS-322 的「21 器件」处方在本项目历史上【从未被单变量实跑过】⇒ ⇒ 这是 S8「归零可达?」这题唯一的下一步
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1215"

BRIEF_325 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-325_hw_s8_leftupper_layout_rehearsal.md"),
    encoding="utf-8").read()
CONT_323 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-323_sw_s1_samebatch_rename_list_cont1.md"),
    encoding="utf-8").read()
CONT_324 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-324_mech_d_led_g_placement_cont1.md"),
    encoding="utf-8").read()

TITLE_325 = (
    "★★[主线内·PCB 线·沙盒预演 / 作业包类·内部活] ★★【「板只改一次」那一趟的 S8 前置: "
    "「左上布局」21 器件 (10×R_SEL_* + 10×TP_DSI_*) 钉位沙盒预演 —— 把 ISS-322 的处方第一次真正单变量实跑一遍 "
    "(三方对照 unc / 网名集合差集 / 名单制闸 / 段内 P-N 翻转) ⇒ 回答「S8 归零到底可达不可达」】★★ "
    "⇒ ★**纯沙盒预演 · 零写板 · 零落表 · 零改闸 · 零改生成器代码** ★"
)

NOTE_325 = (
    "★**2026-11-18 12:1x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 "
    "(status 直接落 fixing ⇒ 下一轮 in_flight 规则会跳过 hw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
    "★**开单依据 (★main 12:1x 本机实读·不抄任何 agent 报告★)**: "
    "★**① ISS-322 已 verified (12:1x)** ⇒ 它的 S8 判决书 = 「(a) 几何可布」+ 「★**但 S8 必须带一次布局修正 "
    "(21 个器件挪到左上 x 5.50..38.35) 且必须与 S1/S2/S3/S4/S6/S7 同趟**★」⇒ ⇒ **那 21 个器件的落位就是 S8 归零的前置** ★ "
    "★**② ★★本单存在的理由 (★main 查遍 53 个臂脚本得到的★)**: `grep -rn \"TP_DSI\" state/ --include=\"*.sh\"` "
    "⇒ **只有 v58 / v69 两个臂钉过 `TP_DSI_*`, 且是在 y=8.80 的另一组坐标 (跟左上无关)** ⇒ ⇒ "
    "⇒ **ISS-322 的「21 器件」处方在本项目历史上【从未被单变量实跑过】⇒ ⇒ 这一趟就是【第一次】** ★ "
    "★**③ 「归零」至今只是推算**: ISS-322 §3-8 逐字写「★**盘上 11 份 DRC JSON 最低 = 23, 无一份 = 0**★」"
    "⇒ ⇒ **S8 能不能真的归零, 现在没有任何实测支撑** ⇒ ⇒ 这一趟就是去把它变成实测 (★跑出 0 是意外之喜, 跑不出 0 也是有价值的实测★) ★ "
    "★**④ 本单目标坐标不手抄**: main 从 `state/.lastgood/best_unc23_clrfix.kicad_pcb` (★unc 23 · 左上限序 · 2026-11-11★) "
    "机器读出 20 个器件的封装原点 (★R_SEL_* y=3.00 · TP_DSI_* y=6.20 · 唯一例外 `TP_DSI_D0_N` 在 (41.55,3.00)★) ⇒ 任务书要求 agent 自己机器读一遍 ★ "
    "★**⑤ ★★三个写盘陷阱 (★main 实读源码确认★)**: (a) `state/gen_pcb_netlist_board.py` 的 `REPORT` 默认写 "
    "**`HW/PCB/PCB_NETLIST_FILL.txt`** ⇒ 必须设 `PCB_REPORT=/tmp/...` (★盘上 53 个臂脚本没有一个设过它·历史臂都覆盖过那个文件★) "
    "(b) **绝不许设 `PCB_ALLOW_OFFICIAL=1`** (c) **`PCB_OUT` 必须以 `.kicad_pcb` 结尾** (★否则生成器 L56~L70 直接 exit(3) 秒退·v69 那轮白跑 6 小时的前车之鉴★) ★ "
    "★**⑥ `.layout_done.json` 不会被污染**: 生成器 L520~L526 显式守卫 ⇒ 非官方板 ⇒ 不写 ⇒ 阶段门 G1 读的 unc=45 一个字节都不动 ★ "
    "★**⑦ ★★一个必须订正的读数 (★main fresh DRC 实跑发现的★)**: ISS-322 §3-6 那张 lane 序对照表的 unc 列**不是全部 fresh 测的** "
    "(`logs/iss322/scripts/probe_lane_order_vs_unc.py` 把 unc **硬编码**在脚本里) ⇒ main 对同一块板 "
    "(md5 `5a5197152157a70b19fbe1365283915c`) fresh 跑 DRC 得 **unc = 29 (不是表里的 26)** ⇒ ⇒ **那一列是历史记录, 不是可复现的 fresh 读数** "
    "⇒ ⇒ 任务书要求本单每个数都自己 fresh 测一遍 ★ "
    "★**⑧ ★★生成器代码比参照板新 ⇒ 本单读数是【新数据点】, 不许宣称「复现了 unc 23」★**: "
    "`state/gen_pcb_netlist_board.py` mtime = 2026-11-17 05:16 晚于 `best_unc23_clrfix.kicad_pcb` (2026-11-11 04:43) ★ "
    "★**⑨ 配方照抄 `state/v76mz_arms.sh` 的 env 逐字节不变** (★唯一变量 = `PCB_PART_POS` 多 10 个 `TP_DSI_*`★) + "
    "预留串只读复用 `state/.lastgood/v76mg_reserve.txt` (★md5 `1950683f8f2981eb6e1141c3559c02a6`★) ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-325_hw_s8_leftupper_layout_rehearsal.md` "
    "(★`python3 state/check_brief_commands.py --brief-file <它>` ⇒ rc=0·★派活前已过命令存在性守卫★) ★ "
    "★**边界**: 零写板 · 零落表 · 零改闸/零改生成器代码 · 零改既有文档正文 · 沙盒只写 `tmp/` + `logs/iss325/` · "
    "只写 `state/fragments/hw.yaml` · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料·需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案★) · "
    "不替老板拍板 (★G7 `iss322_s8_rsel_lane_order` 的落板归 main + 老板★) · 不自签 issue_log ★"
)

VERIFY_322 = (
    "✅ verified (★main 2026-11-18 12:1x 独立复核·不抄 agent 报告★) ⇒ "
    "★**交卷物在盘**: `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` (64,052 B · **544 行** · §0~§7 七节全在 · 占位符 0) + "
    "`HANDOFF/2026-11-18_hw-lead_ISS322_S8布线归零作业包.md` (27,804 B · **254 行** · B0~B6 齐全 · 占位符 0) + "
    "`logs/iss322/` (**31 件**: 30 份 raw + `scripts/` 10 个只读探针) + "
    "`state/fragments/hw.yaml` (★`iss322|ISS-322` 命中 **35**·已写·needs `iss322_s8_*` **7** 条·status=delivered/100/green★) ★ "
    "⇒ ★**悬空引用 = 0** (★main 实测: 交付页引 21 个 `logs/iss322/` 路径 + 交卷页引 27 个 ⇒ 全部真实存在★) ★ "
    "⇒ ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节不变 ★ "
    "⇒ ★**闸链本机实跑**: `state/gate_check.py` ⇒ **rc=0** · Q1 **18/18** · Q6 通过 · Q7 钉板 md5 闸链 **9/9 全绿** · "
    "`state/merge.py` ⇒ rc=0 (产出 655 · 阻塞 43 · 未闭合需求 330 · 冲突 0) · `state/issue_check.py` ⇒ rc=0 · "
    "`state/compare_arm_official.py --self-test` ⇒ **ALL TESTS PASS** rc=0 ★ "
    "★**★本单最值钱的两条结论 (★main 已逐条核过, 老板 G7 的依据★)**: "
    "★**① 它【推翻】了 ISS-265 §0 的处方方向**: ISS-265 说「钉左上 ⇒ lane 序完全反向 ⇒ 要钉右上 (方案 A)」, "
    "而实测 8 块同代板的 lane 序 vs unc 对照 (★`logs/iss322/22_lane_order_vs_unc.txt`★) 显示 "
    "**lane 序与 SoM 端序一致的 7 块板 unc = 23/26/28/29/29/35/35, 唯一 lane 序反的现役板 = 45 (全盘最差)** ⇒ "
    "⇒ **方向反了 ⇒ 修法是把 21 个器件挪到左上, 不是右上** ★ "
    "★**② 「官方板 18092」= 现役板本身 (★段数 18092 / 孔数 433 实测★) ⇒ 43/43 网名签名相同 ⇒ **零区分度** ⇒ "
    "⇒ **它是【自证】不是【旁证】** ⇒ 作业包把它从「几何级旁证」降级成【标记列】(★这条订正不许被改回去★) ★ "
    "★**③ 「归零」至今只是推算**: 本单逐字写「★**盘上 11 份 DRC JSON 最低 = 23, 无一份 = 0**★」⇒ ⇒ **零可达 = [0数据]** ★ "
    "★**交卷页自己声明的未完项如实留账 (不装完成)**: 7 条 need (`iss322_s8_p7_zero_scope` / `iss322_s8_rsel_lane_order` / "
    "`iss322_s8_csi_cap_side` / `iss322_s8_a1_batdet` / `iss322_s8_w1w2_esd` / `iss322_s8_w4_qpg` / `iss322_s8_d_led_g_pos`) "
    "⇒ **归 main + 老板, 本单不代拍** ⇒ ★**续单已开 = ISS-325 (把「左上布局」第一次真跑一遍 · 12:1x 直接派出)** ★"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        # ★锁内重读 (★不许用锁外读到的旧内容写回★)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []

        # ---------- ① ISS-322 → verified ----------
        i322 = idx.get("ISS-322")
        if i322 and i322.get("status") != "verified":
            i322["status"] = "verified"
            i322["verify_date"] = NOW
            i322["verify_by"] = "main"
            i322["verify_result"] = VERIFY_322
            i322["note"] = (i322.get("note") or "") + (
                f"\n★**{NOW} 12:1x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
                "★**独立复核**: 交付页 544 行 §0~§7 + 交卷页 254 行 B0~B6 + 占位符 0/0 + 悬空引用 0 + "
                "`logs/iss322/` 31 件 + 分片命中 35 (needs 7) + 板 md5/mtime 逐字节不变 + "
                "★**闸链本机实跑全绿 (gate rc=0 · Q1 18/18 · Q7 9/9 · merge rc=0 · issue_check rc=0 · "
                "compare_arm_official --self-test ALL TESTS PASS)** ★ "
                "★**本单推翻的两条既有结论已留账**: ① ISS-265 §0 的处方方向 (⇒ 改成挪左上) ② 「官方板同病」降级成标记列 (⇒ 自证不是旁证) ★ "
                "★**未完项如实留账**: 7 条 need 归 main + 老板 (不代拍) ⇒ **续单 ISS-325 已开并派出 (把「左上布局」第一次真跑一遍)** ★")
            applied.append("ISS-322 fixing → verified (main 独立复核)")
        elif i322:
            applied.append("ISS-322 已是 verified (跳过)")

        # ---------- ② ISS-323 cont1 ----------
        i323 = idx.get("ISS-323")
        if i323:
            tb = i323.get("task_brief") or ""
            if "ISS-323 · sw-lead · ★★cont1 续做" not in tb:
                i323["task_brief"] = tb + "\n\n---\n\n" + CONT_323
                applied.append("ISS-323 task_brief += cont1 (★原 brief 全文保留★) · status 保持 fixing")
            i323["dispatched_at"] = NOW
            i323["note"] = (i323.get("note") or "") + (
                f"\n★**{NOW} 12:1x · cron fb67af40 续做重派 cont1** ★ ★**为什么**: 子会话 11:46 起 · "
                "★**12:0x 被父 cron run 连带 abort (status=timeout · abortedLastRun=true · runtimeMs=1438900)**★ "
                "⇒ **它的工作在【写分片那一步】被打断** ⇒ ★**main 12:1x 实读: 交付物 ①②③ 全在盘 "
                "(主文档 73,571 B · 交卷页 32,099 B · logs/iss323 106 件)· 但 `state/fragments/sw.yaml` "
                "mtime = 11:12:06 ⇒ 早于本单开工 ⇒ 一字未写** ⇒ ★**只剩 3 件小事: ① 补写分片 (frag_write.py·原子写) "
                "② 修主文档 §4 标题的 2 个乱码字节 (U+FFFD → 「属」) ③ 重跑闸链并把最新输出贴进交卷页** ⇒ "
                "★**status 保持 fixing** (★不回滚成 open ⇒ 下一轮 in_flight 规则跳过 sw-lead ⇒ 无重复派活窗口★) ★")
        else:
            applied.append("ISS-323 不存在 (★异常★)")

        # ---------- ③ ISS-324 cont1 ----------
        i324 = idx.get("ISS-324")
        if i324:
            tb = i324.get("task_brief") or ""
            if "ISS-324 · mech-lead · ★★cont1 续做" not in tb:
                i324["task_brief"] = tb + "\n\n---\n\n" + CONT_324
                applied.append("ISS-324 task_brief += cont1 (★原 brief 全文保留★) · status 保持 fixing")
            i324["dispatched_at"] = NOW
            i324["note"] = (i324.get("note") or "") + (
                f"\n★**{NOW} 12:1x · cron fb67af40 续做重派 cont1** ★ ★**为什么**: 子会话 11:46 起 · "
                "★**12:0x 同样被父 cron run 连带 abort (status=timeout · abortedLastRun=true · runtimeMs=1156074)**★ "
                "⇒ **它做完的是【算】, 没做完的是【写】** ⇒ ★**main 12:1x 实读: 读数全在 `logs/iss324/` (20 件·"
                "含候选终表 C1~C6 七个字段全填)· 但交付物 ①② + 分片【一个都不在盘上】** ⇒ "
                "★**本单只剩 3 件写卷活: ① `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` §0~§9 ② 交卷页 B0~B6 ③ 分片** ⇒ "
                "★**status 保持 fixing** (★不回滚成 open ⇒ 无重复派活窗口★) ★ "
                "★**main 12:1x 额外查出一条要 agent 自己订正的读数**: `logs/iss324/05_candidates.log` 里 C1/C4 的"
                "「最近邻器件净距 0.000 mm」与 main 用 pcbnew 直读现役板的复算 (★`C_KEY_CAM` 1.273 mm · `R_LED_G.2` 0.949 mm · "
                "`TP_LED_G.1` 2.702 mm★) 对不上 ⇒ 已在 cont brief 里点名 ⇒ **不许把 0.000 照抄进交付页当结论** ★")
        else:
            applied.append("ISS-324 不存在 (★异常★)")

        # ---------- ④ 新开 ISS-325 (hw-lead · status 直接落 fixing) ----------
        if "ISS-325" not in idx:
            issues.append({
                "id": "ISS-325",
                "title": TITLE_325,
                "owner": "hw-lead",
                "status": "fixing",
                "severity": "high",
                "reporter": "main",
                "raised": NOW,
                "due": "2026-11-19",
                "created_at": NOW,
                "dispatched_at": NOW,
                "verify_by": "main",
                "source_blocker": "ISS-322",
                "task_brief": BRIEF_325,
                "note": NOTE_325,
                "need_keys": [
                    "iss325_s8_zero_reachability",
                    "iss325_s8_leftupper_rehearsal_scope",
                ],
            })
            applied.append("ISS-325 开单 (status=fixing ⇒ 已派)")
        else:
            applied.append("ISS-325 已存在 (跳过)")

        # ---------- ⑤ 落盘 issue_log (原子) ----------
        out = dict(log)
        out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_land322_cont323_cont324_open325" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        # ---------- ⑥ dispatch_log ----------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        for iid, agent, note in (
            ("ISS-323", "sw-lead",
             "★**cont1 续做重派** (★上一趟 12:0x 被父 run 连带 abort·只差【写分片 + 1 处乱码 + 重跑闸链】·status 保持 fixing★)"),
            ("ISS-324", "mech-lead",
             "★**cont1 续做重派** (★上一趟 12:0x 被父 run 连带 abort·只差【交付物 ①② + 分片】·status 保持 fixing★)"),
            ("ISS-325", "hw-lead",
             "★**新开并直接派出** (★status=fixing ⇒ 下一轮 in_flight 规则跳过 hw-lead ⇒ 无重复派活窗口★)"),
        ):
            if not any(isinstance(d, dict) and d.get("issue") == iid and "12:1x" in str(d.get("brief"))
                       for d in disp):
                disp.append({
                    "issue": iid, "agent": agent, "at": NOW, "brief": note,
                    "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 12:1x · "
                            "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
                })
                applied.append("dispatch_log 追加 %s" % iid)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_land322_cont323_cont324_open325" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))

        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
