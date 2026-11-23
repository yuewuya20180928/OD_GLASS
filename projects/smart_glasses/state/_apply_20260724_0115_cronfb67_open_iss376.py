#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0115_cronfb67_open_iss376.py
==================================================
cron fb67af40 (ARS45 队列自动派活) · 开 ISS-376 (hw-lead) + 记录 ISS-374/ISS-375 复活重派
★**铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★**
★写回用【文本追加】(★不全文件 yaml 重排·实测全文件重排会把已签收单的 verify_result 折行重排·属 churn★)
★flock + 备份 + 写回自检 ⇒ 前 N 条逐条不变
"""
import fcntl
import os
import shutil
import sys
import tempfile
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = time.strftime("%Y%m%d_%H%M")
BRIEF_PATH = "state/dispatch_briefs/ISS-376_hw_jdebug_land_fit.md"

BRIEF = open(os.path.join(PROJ, BRIEF_PATH), encoding="utf-8").read()

NEW = [
    {
        "id": "ISS-376",
        "title": ("★★[★新主线·PCB 线·HW 侧·「板那一趟」`J_DEBUG` 换官方 1×4 THT land 的**落位可行性**穷举（现位放不进 ⇒ 挪哪 / 挪多大 / 挪完还剩什么）·纯分析+沙盒预演+新建闸·零写板] "
                  "★★【★main 2026-11-24 00:5x~01:0x 本机实读+本机实算 (★不抄任何 agent 报告★): ★**ISS-373 沙盒 S2b 实测: 官方 1.27mm 4×THT land 放不进 `J_DEBUG` 现位** ⇒ ★**PTH pad1 (144.3000,58.0000) vs via `JTAG_TDO` (143.7000,57.9500) 孔净距 `0.1271` (要求 ≥`0.25`) · PTH pad3 (146.8400,58.0000) vs via `XTAL_OUT` (146.9500,57.9500) 孔净距 `0.0000`** ⇒ ★**⇒ DRC `hole_to_hole` 由 `0` → `4`** ⇒ ★**⇒ 「那一趟换 91 件」这条路卡死在一个具体的物理点上** ⇒ ★**本单 = 把【挪哪 / 挪多大 / 挪完还剩什么】三个问题用机器算出来, 交 main 裁「那一趟换不换 land (90 件 vs 91 件)」**★ ★★"
                  "★★**开单依据**: ① ★**ISS-373 (hw-lead) 已于 2026-11-24 00:5x 由 `state/_apply_20260724_0050_cronfb67_sign_iss373.py` 独立复核签收 verified (★37 条验收线全绿 + 自测 7/7★) ⇒ ★**hw-lead 槽位空出来** ★ ② ★**兄弟 job 775d9893 于 2026-11-24 00:24:07 被【cron 执行超时 (60 分钟硬墙·externalAbort=true)】掐死, 它的下一轮 01:24 才到 ⇒ ★**这一小时 hw-lead 无活可干** ★ ③ ★**ISS-373 的沙盒已把死结定位到具体坐标, 但「挪哪 / 挪多大 / 挪完还剩什么」这三问【全项目至今没有一份机器算出来的答案】⇒ ★**这是「板只改一次」那一趟开工前的必要前置** ★ ★★"
                  "★★**类别**: ★**纯分析 + 沙盒预演 + 新建闸 · 零写板 · 零落表 · 零改既有闸/既有页面 · 新闸零挂链 · 不代拍** ★★"),
        "severity": "high",
        "source_blocker": "ISS-373",
        "source_agent": "main",
        "desc": ("★**题**: ★**ISS-373 的沙盒实测把「那一趟换 91 件」这条路卡死在一个具体的物理点上** ⇒ ★**本单要交的是【可行区】(哪一段区间放得下) + 【最优落点】(带余量) + 【挪完还剩什么】(逐件带坐标的代价清单), 交 main 裁** ★★\n"
                  "★**① 现位 (板读)**: ★**封装原点 (144.3000, 58.0000) · orient 0.0 · 4 个 pad 全 SMD 0.2750×0.9000 全 shape=1 (RECT) · pad X = 142.2000/142.7000/143.2000/143.7000 (pitch 0.5000) · net = JTAG_TCK/JTAG_TMS/JTAG_TDI/JTAG_TDO · 铜箔 X 142.0625..143.8375 (宽 1.7750) × Y 56.1500..57.0500 (0.9000) · fab 名义 6.00×4.00**★\n"
                  "★**② 官方 1×4 THT land 实读**: ★`.../Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ⇒ ★**pad\"1\" thru_hole rect (at 0 0) size 1×1 drill 0.65 · pad\"2\" thru_hole circle (at 0 1.27) · pad\"3\" (at 0 2.54) · pad\"4\" (at 0 3.81) ⇒ 四 pad 沿局部 Y 排, 跨度 3.81 · F.CrtYd fp_rect (-1.55 -1.14)..(1.55 4.95) = 3.10×6.09 · F.Fab 线框 X -1.05..1.05 / Y -0.635..4.445 = 2.10×5.08**★\n"
                  "★**③ 板 DRC 约束 (读 .kicad_pro 真值)**: ★**min_hole_to_hole = 0.25 · min_hole_clearance = 0.25 · min_through_hole_diameter = 0.3 · min_via_diameter = 0.5 · min_via_annular_width = 0.1 · min_track_width = 0.2**★\n"
                  "★**④ 死结 (ISS-373 沙盒 S2b 实测)**: ★**PTH pad1 (144.3000,58.0000) vs via JTAG_TDO (143.7000,57.9500) 孔净距 0.1271 · PTH pad3 (146.8400,58.0000) vs via XTAL_OUT (146.9500,57.9500) 孔净距 0.0000 ⇒ hole_to_hole 由 0 → 4**★\n"
                  "★**⑤ 附近过孔 (main 00:4x 实读)**: ★**XTAL_OUT (142.2000,53.2000) 与 (146.9500,57.9500) · JTAG_TDO (143.7000,57.9500) 与 (142.4500,54.7000) · JTAG_TCK (138.7000,54.7000) · JTAG_TMS (145.2000,54.9500) 与 (147.2000,54.4500) · XTAL_IN (141.2000,58.9500) · 全部 via 直径 0.6000 / 钻孔 0.3000**★\n"
                  "★**⑥ 新 land 铜箔 X 宽 = 4.8100 (3×1.27+1.00) ⇒ 比现位 1.7750 宽出 3.0350**★\n"
                  "★**⑦ ISS-373 实测: 落盘后 KiCad 连通性重建把 63 段 JTAG_TDO 走线改归 JTAG_TCK ⇒ 那 4 条 JTAG 走线端点脱网 ⇒ 必须重接**★\n"
                  "★**⑧ 结构侧账 (ISS-371 已算·不归本单)**: ★**J_DEBUG 换官方 land 后 必须清空区 X 宽 4.0850→4.8100, 最外侧焊盘每边超出清空区 0.3625 ⇒ 铜箔进清空区, 但方向仍过 CRIT 0.60 (余量 3.99×) ⇒ ★**板侧挪落位不会把结构侧方向推翻 ⇒ 本单只答【板侧能不能挪得下 + 挪完还剩什么】**★\n"),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss373_jdebug_swap_or_not"],
        "task_brief": BRIEF,
        "note": ("★2026-11-24 01:1x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★ "
                 "★ **开单依据 (本机实读+实算, 不抄任何 agent 报告)**: ① ★**ISS-373 (hw-lead) 已于 2026-11-24 00:5x 独立复核签收 verified (★签收闸 `state/_apply_20260724_0050_cronfb67_sign_iss373.py` · 37 条验收线全绿 + 自测 7/7★) ⇒ ★**hw-lead 槽位空出来** ★ "
                 "② ★**兄弟 job 775d9893 于 2026-11-24 00:24:07 被【cron 执行超时 (60 分钟硬墙·externalAbort=true·lastDurationMs=3,606,068)】掐死, 下一轮 01:24 才到 ⇒ ★**这一小时 hw-lead 无活可干** ★ "
                 "③ ★**ISS-373 沙盒 S2b 已把「换 91 件」的死结定位到具体坐标 (孔净距 0.1271 / 0.0000), 但【挪哪/挪多大/挪完还剩什么】三问至今无机器答案** ⇒ ★**这是「板只改一次」那一趟开工前的必要前置** ★ "
                 "④ ★**本单是 PCB 线纯分析/沙盒类 (不动板)** ⇒ 符合「板只改一次」纪律 ① (★先派纯分析/作业包类★) ★ "
                 "★ **任务书全文**: `state/dispatch_briefs/ISS-376_hw_jdebug_land_fit.md` (★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★"),
        "dispatched_at": "2026-11-24",
    },
]

# ★★ISS-374 / ISS-375 的复活重派记录 (★status 保持 fixing 不动 ⇒ 零 churn ⇒ 兄弟 job 看不见★) ★★
REDISPATCH = [
    {
        "issue": "ISS-374",
        "agent": "mech-lead",
        "at": "2026-11-24 01:1x",
        "cont": "cont1",
        "dead_cause": ("★cont0 (会话 `agent:mech-lead:subagent:3c223dbe` / sessionId 63571d93) 于 2026-11-23 23:23:13 被掐死 "
                       "(★sessions_list: status=timeout + abortedLastRun=true + runtimeMs=394,308 ≈ 6.6 分钟·promptError=\"This operation was aborted\"·"
                       "**externalAbort=false** ⇒ 非外部 abort ⇒ 是【父 run (fb67af40 22:39~23:18 那趟) 收尾连带杀掉】·非上下文溢出·非逻辑错★) ⇒ "
                       "★**三件交付物一件没落** (★`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` 不存在 · `MECH/check_juart_1p27_clearance.py` 不存在 · "
                       "交卷页不存在 · `state/fragments/mech.yaml` 里 `iss374` 命中 = 0·`logs/iss374/` 空)★ ⇒ ★**⇒ 僵尸 fixing, 必须复活**★"),
        "brief": ("★**cont1 续做** (★不是从零重做★) ⇒ ★**完整任务书 = `state/dispatch_briefs/ISS-374_mech_juart_1p27_clearance_truth_cont1.md` "
                  "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ⇒ ★**原任务书全文 = `state/dispatch_briefs/ISS-374_mech_juart_1p27_clearance_truth.md` (★仍有效★)★ "
                  "★ **本 job 追加的三条订正 (★都是 main 本机实读·不抄任何 agent 报告★)**: ① ★**上一趟把 6.6 分钟全花在读资料上** ⇒ ★**cont1 brief 的 §一 已把全部板面读数/官方 land 实读/判据常量/座体清空区坐标逐条给出** ⇒ ★**第一个工具调用就应该是写沙盒测量脚本跑 S0, 不是读文档** ★ "
                  "② ★**`J_DEBUG` 的「必须清空区 X 宽」是【铜箔宽支配】, `J_UART` 的是【座体宽支配】⇒ ★**两颗件推导链不同源** ⇒ ★**不许把 J_DEBUG 的推导链套到 J_UART 上** (★闸 J5 防的就是这个★) ★ "
                  "③ ★**重活与交付物不许同趟** (★子会话有一条约 16 分钟的硬墙·实测三趟续做会话都被掐在这附近★) ⇒ ★**先落盘读数 → 写页 → 写闸 → 交卷页 + 分片**, 每步先落盘 ★ ★ "
                  "★ **status 全程保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 撞车窗口 0★) ★ "
                  "★ **子会话键**: `agent:mech-lead:subagent:85817535-54bf-4d4e-988d-4b9a52ac62d9` · runId `ca0828a4-ee4c-4566-804b-8de8a8aba4e5` · taskName `queue_iss374_cont1` ★"),
        "session_key": "agent:mech-lead:subagent:85817535-54bf-4d4e-988d-4b9a52ac62d9",
        "run_id": "ca0828a4-ee4c-4566-804b-8de8a8aba4e5",
        "task_name": "queue_iss374_cont1",
        "dispatched_at": "2026-11-24 01:1x",
        "prev_session_key": "agent:mech-lead:subagent:3c223dbe-63fd-4a46-a18a-36529f1d0f59",
        "redispatch_zombie": "True",
        "zero_delivery": "True",
        "partial_delivery": "0/3 交付物 (★连 logs/iss374/ 都是空的·只有 /tmp/iss374_*.py 三个一次性读板脚本在盘★)",
        "status_note": "台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 给 mech-lead 再派活 ⇒ 零撞车窗口",
    },
    {
        "issue": "ISS-375",
        "agent": "sw-lead",
        "at": "2026-11-24 01:1x",
        "cont": "cont1",
        "dead_cause": ("★cont0 (会话 `agent:sw-lead:subagent:0d87082c` / sessionId 570e20e2) 于 2026-11-23 23:23:11 被掐死 "
                       "(★sessions_list: status=timeout + abortedLastRun=true + runtimeMs=387,911 ≈ 6.5 分钟·promptError=\"This operation was aborted\"·"
                       "**externalAbort=false** ⇒ 非外部 abort ⇒ 是【父 run (fb67af40 22:39~23:18 那趟) 收尾连带杀掉】·非上下文溢出·非逻辑错★) ⇒ "
                       "★**三件交付物一件没落** (★`SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` 不存在 · `SW/tools/check_debug_pin_order_contract.py` 不存在 · "
                       "交卷页不存在 · `state/fragments/sw.yaml` 里 `iss375` 命中 = 0★) ⇒ ★**⇒ 僵尸 fixing, 必须复活**★"),
        "brief": ("★**cont1 续做** (★不是从零重做★) ⇒ ★**完整任务书 = `state/dispatch_briefs/ISS-375_sw_debug_pin_order_contract_cont1.md` "
                  "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ⇒ ★**原任务书全文 = `state/dispatch_briefs/ISS-375_sw_debug_pin_order_contract.md` (★仍有效★)★ "
                  "★ **本 job 追加的三条订正 (★都是 main 本机实读·不抄任何 agent 报告★)**: ① ★**沙盒 builder 有真缺陷**: `tmp/iss375_sbx/iss375_build.py` 里 `p.SetNetCode(...)` 写在 `b.Add(fp)` 【之前】 ⇒ "
                  "★**SetNetCode 对还没挂到板上的封装是空操作 ⇒ net code 静默丢失** ⇒ ★**盘上 `logs/iss375/meas_J_DEBUG_s1_jdebug_rot90.json` 里四个 pad 的 `net` 全是 `\"\"`** ★ "
                  "⇒ ★**本趟第一件事 = 把 SetNetCode 挪到 b.Add(fp) 之后, 再重建 S1/S2** ★ "
                  "② ★**`tmp/iss375_sbx/s2_jdebug_rot270.kicad_pcb` 的 md5 = `611b869e…` = 跟真板逐字节相同 ⇒ ★**rot270 那块板压根没建出来** (★上趟死在 S1 之后★) ⇒ ★**必须重建** ★ "
                  "③ ★**四条已在盘上证完的事不要重做**: ★**rot90 ⇒ pad1 在 X 最小端 (顺排 TCK→TDO, pad X = 141.0450/142.3150/143.5850/144.8550) · rot270 ⇒ pad1 在 X 最大端 (逆排, pad X 集合与 rot90 逐字相同) · 官方 land pad1 = `thru_hole rect` 而 pad2/3/4 = `thru_hole circle` (⇒ 换官方 land 后板面【第一次】出现 pin1 方形标记) · 现状板面四个 pad 全 SMD 全 RECT (无 pin1 标记)** ⇒ ★**把时间投到交付物上** ★ "
                  "★ **重活与交付物不许同趟** (★子会话有一条约 16 分钟的硬墙★) ⇒ ★**先落盘读数 → 写页 → 写闸 + selftest → 交卷页 + 分片** ★ ★ "
                  "★ **status 全程保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 撞车窗口 0★) ★ "
                  "★ **子会话键**: `agent:sw-lead:subagent:4c87e4ad-f092-4f3a-a230-dc98a348e228` · runId `9a397a46-b97c-4d77-a6dc-20015df6d71a` · taskName `queue_iss375_cont1` ★"),
        "session_key": "agent:sw-lead:subagent:4c87e4ad-f092-4f3a-a230-dc98a348e228",
        "run_id": "9a397a46-b97c-4d77-a6dc-20015df6d71a",
        "task_name": "queue_iss375_cont1",
        "dispatched_at": "2026-11-24 01:1x",
        "prev_session_key": "agent:sw-lead:subagent:0d87082c-63fd-4a3c-91e3-c411c95f4037",
        "redispatch_zombie": "True",
        "zero_delivery": "True",
        "partial_delivery": "0/3 交付物 (★但 `tmp/iss375_sbx/` 7 件 + `logs/iss375/` 5 件沙盒半成品在盘 ⇒ 续做不是从零★)",
        "status_note": "台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 给 sw-lead 再派活 ⇒ 零撞车窗口",
    },
    {
        "issue": "ISS-376",
        "agent": "hw-lead",
        "at": "2026-11-24 01:1x",
        "job": ("cron fb67af40 (ARS45 队列自动派活) · ★本 job 步骤 2 的动作: ★**开单 + 直接落 fixing + spawn** "
                "(★铁律⑩-i 先落 fixing 再 spawn⇒兄弟 job 读同一字段⇒零撞车窗口★) · "
                "★**开单依据 = ISS-373 签收后 hw-lead 槽位真空 + 兄弟 job 775d9893 00:24:07 被 cron 60 分钟硬墙掐死 (下一轮 01:24) + "
                "ISS-373 沙盒已把「换 91 件」的死结定位到具体坐标但【挪哪/挪多大/挪完还剩什么】三问至今无机器答案**★"),
        "brief": ("★**开单依据 (本机实读+实算, 不抄任何 agent 报告)**: ① ★**ISS-373 (hw-lead) 已于 2026-11-24 00:5x 独立复核签收 verified** ⇒ ★**hw-lead 槽位空出来** ★ "
                  "② ★**兄弟 job 775d9893 于 00:24:07 被 cron 执行超时掐死 (60 分钟硬墙·externalAbort=true·lastDurationMs=3,606,068·consecutiveErrors=8) ⇒ 下一轮 01:24 才到** ⇒ ★**这一小时 hw-lead 无活可干** ★ "
                  "③ ★**ISS-373 沙盒 S2b 实测: PTH pad1 vs via JTAG_TDO 孔净距 0.1271 · PTH pad3 vs via XTAL_OUT 孔净距 0.0000 ⇒ hole_to_hole 0→4 ⇒ 「换 91 件」卡死在一个具体物理点上** ★ "
                  "④ ★**本单 = 纯分析+沙盒+新建闸 (零写板) ⇒ 符合「板只改一次」纪律 ① (先派纯分析/作业包类)** ★ "
                  "★ **任务书全文**: `state/dispatch_briefs/ISS-376_hw_jdebug_land_fit.md` (★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★"),
    },
]


def atomic_write(path, text):
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


def main():
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_%s_cronfb67_openiss376" % STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_%s_cronfb67_openiss376" % STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        # ---------- issue_log: 文本追加 ----------
        orig_log = open(LOG, encoding="utf-8").read()
        log = yaml.safe_load(orig_log) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        blocks = []
        for new in NEW:
            iid = new["id"]
            if iid in idx:
                it = idx[iid]
                it["status"] = new["status"]
                it["task_brief"] = new["task_brief"]
                it["note"] = new["note"]
                it["dispatched_at"] = new["dispatched_at"]
                applied.append("%s 已存在 ⇒ status→fixing + brief/note 刷新 (幂等)" % iid)
                continue
            blk = yaml.safe_dump([new], allow_unicode=True, sort_keys=False,
                                 width=100, default_flow_style=False)
            assert blk.startswith("- id:"), blk[:80]
            blocks.append(blk)
            applied.append("新开 %s (owner=hw-lead) · status 落 fixing (★先落 fixing 再 spawn⇒零撞车窗口★)" % iid)

        if blocks:
            out = orig_log.rstrip("\n") + "\n" + "".join(blocks)
            atomic_write(LOG, out)
        else:
            out = orig_log

        back = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        after = back.get("issues") or []
        if len(after) != len(issues) + len(blocks):
            raise SystemExit("★issue_log 写回条数不对: 期望 %d, 实际 %d"
                             % (len(issues) + len(blocks), len(after)))
        if not all(a == b for a, b in zip(issues, after[:len(issues)])):
            raise SystemExit("★issue_log 写回自检失败: 前 %d 条有变动" % len(issues))
        applied.append("issue_log 自检: 前 %d 条逐条不变 + 新增 %d 条 ⇒ OK" % (len(issues), len(blocks)))

        # ---------- dispatch_log: 文本追加 ----------
        orig_dl = open(DLOG, encoding="utf-8").read()
        dl = yaml.safe_load(orig_dl) or []
        dl_is_dict = isinstance(dl, dict)
        entries = dl.get("dispatches") or [] if dl_is_dict else dl
        dl_blocks = []
        for e in REDISPATCH:
            blk = yaml.safe_dump([e], allow_unicode=True, sort_keys=False,
                                 width=100, default_flow_style=False)
            assert blk.startswith("- issue:"), blk[:80]
            dl_blocks.append(blk)
        if dl_blocks:
            out_dl = orig_dl.rstrip("\n") + "\n" + "".join(dl_blocks)
            atomic_write(DLOG, out_dl)
        else:
            out_dl = orig_dl

        back_dl = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        e2 = back_dl.get("dispatches") or [] if dl_is_dict else back_dl
        if len(e2) != len(entries) + len(dl_blocks):
            raise SystemExit("★dispatch_log 写回条数不对")
        if not all(a == b for a, b in zip(entries, e2[:len(entries)])):
            raise SystemExit("★dispatch_log 写回自检失败: 前 %d 条有变动" % len(entries))
        applied.append("dispatch_log 自检: 前 %d 条逐条不变 + 新增 %d 条 ⇒ OK" % (len(entries), len(dl_blocks)))
        applied.append("dispatch_log 新增: ISS-374 cont1 复活 / ISS-375 cont1 复活 / ISS-376 开单")

    print("=" * 78)
    print("★ cron fb67af40 · 开单 + 复活重派落盘 (★文本追加 + flock + 备份 + 写回自检★)")
    for a in applied:
        print("  · %s" % a)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
