#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0300_cronfb67_open_iss377_378.py
==================================================
main (项目总工) 的【开单 + 落 fixing + 派活】· ISS-377 (mech-lead) + ISS-378 (sw-lead)

★**为什么开这两个单 (★本机实读 + 实算 · 不抄任何 agent 报告★)**:
  ★① `python3 state/advance.py --json` 实跑 ⇒ ★**`internal: []`** (★三个总工名下零 open 可派 ⇒ 队列对
  ★   mech / sw 两条线【真断线】★) ⇒ ★**按「开新单」处理**
  ★② ★**ISS-374 (mech-lead) 与 ISS-375 (sw-lead) 已于 2026-11-24 02:4x 由 main 独立复核签收 verified**
  ★   (★签收闸 `state/_apply_20260724_0235_cronfb67_sign_iss374_375.py` · fail-closed · 全绿才签 · 自测 10/10★)
  ★   ⇒ ★**mech-lead / sw-lead 两个槽位同时真空出来** ⇒ ★**名下零 open 项 ⇒ 必须补新单, 否则槽位空转**
  ★③ ★**ISS-376 (hw-lead) 02:25 还在产日志 ⇒ 真在飞 ⇒ 本轮不碰它, hw-lead 槽位保留**

★**两个单的正题来源 (★都是上一趟亲手点出来的病根, 不是本 job 造的口径★)**:
  ★**ISS-377 (mech-lead)**: ISS-374 结论原话 = ★**「两件方向相反, 根因是清空区口径不同源(`J_DEBUG` 铜箔支配
  ★   / `J_UART` 座体支配)」** ⇒ ★**板只改一次 ⇒ 改板前必须把这套口径合成一张表** ★+ ★**座体真实型号至今 `[0数据]`
  ★   (ISS-267 F-8) ⇒ 必须【自己网上查】(★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)**
  ★**ISS-378 (sw-lead)**: ISS-375 交卷页 B5-② = ★**「ISS-344 口径把 `JTAG_TDI` 列进 8 条必需, 而 SoM 侧端点
  ★   实测就是 `SoC_NC`」** ⇒ ★**板要对着一个不再变的网表画 ⇒ 这条冲突必须在改板前收敛** ★

★**纪律 (★铁律⑩-i★)**: ★**先落 `fixing` 再 spawn** ⇒ ★**兄弟 job 775d9893 的 `advance.py --json` 看不见这两条
  ⇒ 撞车窗口 = 0** ★
★**边界**: ★**零写板 · 零落表 · 零外发 · 不代拍 · 零挂链 · 两个单都是【纯分析 / 作业包】类 (不动板)**
  ⇒ ★**符合「板只改一次」纪律 ① (先派纯分析/作业包类)★**
"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
DLOG = os.path.join(PROJ, "state/dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF_377 = "state/dispatch_briefs/ISS-377_mech_connector_clearance_caliber.md"
BRIEF_378 = "state/dispatch_briefs/ISS-378_sw_debug_header_fw_impact.md"

NOTE_377 = (
    "★2026-11-24 02:5x~03:0x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
    "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★ "
    "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
    "(★三个总工名下零 open 可派 ⇒ 队列对 mech 这条线真断线★) ② ★**ISS-374 (mech-lead) 已于 2026-11-24 02:4x "
    "由 main 独立复核签收 verified** (★签收闸 `state/_apply_20260724_0235_cronfb67_sign_iss374_375.py` · "
    "fail-closed · 全绿才签 · 自测 10/10★) ⇒ ★**mech-lead 槽位真空出来** ③ ★**ISS-376 (hw-lead) 02:25 还在产日志 "
    "⇒ 真在飞 ⇒ 本轮不碰它★ ④ ★**本单正题 = ISS-374 亲手点出的病根**: 「两件方向相反, 根因是清空区口径不同源"
    "(`J_DEBUG` 铜箔支配 / `J_UART` 座体支配)」⇒ ★**板只改一次 ⇒ 改板前必须把口径合成一张表** ★+ ★**座体真实型号 "
    "至今 `[0数据]` (ISS-267 F-8) ⇒ 必须自己网上查 (零外发)** ★ "
    "★**类别**: ★**纯分析 / 作业包类** (★老板 2026-11-17 00:43: 目标是绘制 PCB 图 ⇒ PCB 线可派, 但板只改一次 ⇒ "
    "先派不动板的★) ★ **边界**: 零写板 · 零落表 · 零改已签收件 · 零挂链 · 零外发 · 不代拍 ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-377_mech_connector_clearance_caliber.md` "
    "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★"
)

NOTE_378 = (
    "★2026-11-24 02:5x~03:0x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
    "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★ "
    "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
    "(★三个总工名下零 open 可派 ⇒ 队列对 sw 这条线真断线★) ② ★**ISS-375 (sw-lead) 已于 2026-11-24 02:4x "
    "由 main 独立复核签收 verified** (★签收闸 `state/_apply_20260724_0235_cronfb67_sign_iss374_375.py` · "
    "fail-closed · 全绿才签 · 自测 10/10★) ⇒ ★**sw-lead 槽位真空出来** ③ ★**ISS-376 (hw-lead) 02:25 还在产日志 "
    "⇒ 真在飞 ⇒ 本轮不碰它★ ④ ★**本单正题 = ISS-375 交卷页 B5-② 点名的板侧口径冲突**: ISS-344 口径把 `JTAG_TDI` "
    "列进 8 条「必需」单端脚, 而 ★**main 本机实跑**: `HW/RK3572_PIN_TABLE/rk3572_pins.csv` (★官方 datasheet V1.1 解析★) "
    "`grep -i jtag` 命中 4 行**全是 `JTAG_TCK_M0` / `JTAG_TMS_M0` / `JTAG_TCK_M1` / `JTAG_TMS_M1` ⇒ SoC 侧只有 TCK/TMS, "
    "无 TDI/TDO mux 名**; `HW/PCB/FET3572C_PIN_TABLE.csv` (★SoM 对外引脚表 399 数据行★) `grep -ic jtag` = 0 "
    "⇒ 模块侧无 JTAG 引出** ⇒ ★**「板要对着一个不再变的网表画」⇒ 这条冲突必须在改板前收敛 (改口径 / 改网表 / 换 SoM 三选一 + 代价)** ★ "
    "★**类别**: ★**纯分析 / 作业包类** (★不动板·不动网表真源★) ★ **边界**: 零写板 · 零落表 · 零改固件本体 · "
    "零改已签收件 · 零挂链 · 零外发 · 不代拍 (终裁交 main/老板) ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-378_sw_debug_header_fw_impact.md` "
    "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★"
)

DESC_377 = (
    "★**题 (来源 = ISS-374 的交卷结论, 不是本 job 造的口径)★**: ISS-374 实测出 `J_DEBUG` 与 `J_UART` 两颗同族件"
    "换官方 land 后方向相反 ⇒ ★**根因 = 「座体必须清空区」的口径不同源 (`J_DEBUG` 铜箔支配 / `J_UART` 座体支配)** ⇒ "
    "★**那趟换 91 件之前, 净距判据必须先合成同一套公式 + 同一张表**, 否则每换一颗都要重猜一次口径 ★ "
    "★**本机实读 (main 2026-11-24 02:2x~02:5x, 可复跑)★**: `MECH/check_juart_1p27_clearance.py` rc=0 (9/9) · "
    "`MECH/check_jdebug_1p27_clearance.py` rc=0 (7/7) · 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime "
    "`2026-11-06 07:07:17.362193413` / size `4940213` ⇒ 18 天逐字节未动 ★ "
    "★**本单要交三件**: ① 同源表页 (每颗件标「清空区口径来源」+ 每边余量向量) ② 冲突清单 (口径不同源 + 支配方随变体换人) "
    "③ 座体真实型号【自己网上查】(查不到 ⇒ `[0数据]` + 降级方案, 零外发) ⇒ 外加一条新闸 (零挂链) + 交卷页 + 分片 ★"
)

DESC_378 = (
    "★**题 (来源 = ISS-375 交卷页 B5-②, 不是本 job 造的口径)★**: ★**ISS-344 的口径把 `JTAG_TDI` 列进 8 条「必需」"
    "单端脚 (`SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` §7-4 / `ISS344-CORR` 块), 而 ISS-375 实测 `JTAG_TDI_SOC` "
    "的 SoM 侧端点此刻就是 `SoC_NC`** ⇒ ★**「必需」与「SoM 侧不存在」直接对撞** ⇒ ★**板要对着一个不再变的网表画 "
    "⇒ 这条必须先收敛, 否则画出来的板带着一条不存在的信号** ★ "
    "★**main 本机实跑 (2026-11-24 02:5x, 可复跑)★**: `grep -i jtag HW/RK3572_PIN_TABLE/rk3572_pins.csv` ⇒ 4 行, "
    "全是 `JTAG_TCK_M0` / `JTAG_TMS_M0` / `JTAG_TCK_M1` / `JTAG_TMS_M1` ⇒ ★**SoC 侧只有 TCK/TMS** ★; "
    "`grep -ic jtag HW/PCB/FET3572C_PIN_TABLE.csv` ⇒ 0 ⇒ ★**SoM 模块侧无 JTAG 引出** ★ "
    "★**本单要交三件**: ① 逐网固件影响面表 (每条网: 当前 pad / 换 land 后变不变 / 要改哪一行, ★只写行号一行都不许改★) "
    "② 三条救砖链 (USB / UART / JTAG) 的现状与换件后对照 + 最坏只剩哪条链 ③ `JTAG_TDI` 冲突的三条路 (①改口径 ②改网表 "
    "③换 SoM) 各自代价 + 建议 (不代拍) ⇒ 外加一条新闸 (★核心判据: JTAG 事实必须由闸自己跑 grep 实出来★) + 交卷页 + 分片 ★"
)

ISSUES = [
    {
        "id": "ISS-377",
        "title": "★★[新主线·PCB 线·结构侧·「板那一趟」] 座体净距判据**同源化** (`J_DEBUG` 铜箔支配 vs `J_UART` 座体支配 ⇒ 统一成一张表) + 座体真实型号**官网自查找证** (查不到 ⇒ 降级方案)",
        "severity": "high",
        "source_blocker": "ISS-374",
        "source_agent": "mech-lead",
        "desc": DESC_377,
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss374_mech_connector_clearance_caliber_unify",
                      "iss267_mech_connector_housing_real_model_webcheck"],
        "task_brief": open(os.path.join(PROJ, BRIEF_377), encoding="utf-8").read(),
        "note": NOTE_377,
        "dispatched_at": "2026-11-24",
    },
    {
        "id": "ISS-378",
        "title": "★★[新主线·PCB 线·SW 侧·「板那一趟」] `J_DEBUG`/`J_UART` 排针换 land 后的**固件影响面清单** + ★★`ISS-344` 与「SoM 侧无 JTAG 引出」的**板侧口径冲突收敛** (官网自查证)★★",
        "severity": "high",
        "source_blocker": "ISS-375",
        "source_agent": "sw-lead",
        "desc": DESC_378,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss375_sw_debug_header_fw_impact",
                      "iss344_sw_jtag_tdi_som_side_conflict_converge"],
        "task_brief": open(os.path.join(PROJ, BRIEF_378), encoding="utf-8").read(),
        "note": NOTE_378,
        "dispatched_at": "2026-11-24",
    },
]


def dump_entry(e):
    """★把一条 issue 序列化成 YAML 列表项 (★0 缩进 '- id:' + 2 缩进字段★)"""
    txt = yaml.safe_dump({"issues": [e]}, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=100000)
    lines = txt.split("\n")
    assert lines[0].startswith("issues:"), lines[0]
    return "\n".join(lines[1:]).rstrip("\n") + "\n"


def main():
    # ---- 0 前置: 两条 id 不许已存在 ----
    raw = open(LOG, encoding="utf-8").read()
    doc = yaml.safe_load(raw)
    ids = {i.get("id") for i in (doc.get("issues") or [])}
    for e in ISSUES:
        if e["id"] in ids:
            print("★★%s 已存在 ⇒ 停下, 不重复开单" % e["id"])
            return 2

    # ---- 1 先落 issue_log (status=fixing, 铁律⑩-i) ----
    bak = LOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(LOG, bak)
    add = "".join(dump_entry(e) for e in ISSUES)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw.rstrip("\n") + "\n" + add)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    # 校验: 落盘后能解析 + 两条 status 真是 fixing
    doc2 = yaml.safe_load(open(LOG, encoding="utf-8"))
    got = {i.get("id"): i.get("status") for i in (doc2.get("issues") or [])}
    for e in ISSUES:
        assert got.get(e["id"]) == "fixing", (e["id"], got.get(e["id"]))
    print("★ issue_log 已落: ISS-377=fixing / ISS-378=fixing (备份 %s)" % bak)

    # ---- 2 再落 dispatch_log (追加式) ----
    ddoc = yaml.safe_load(open(DLOG, encoding="utf-8"))
    assert isinstance(ddoc, list)
    bak2 = DLOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(DLOG, bak2)
    for e in ISSUES:
        ddoc.append({
            "issue": e["id"],
            "agent": e["owner"],
            "at": "2026-11-24",
            "brief": e["title"],
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★本 job 步骤 2 的动作: ★**开单 + 直接落 fixing + spawn** "
                    "(★铁律⑩-i 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) · "
                    "★**开单依据 = ISS-374/ISS-375 于 02:4x 被 main 独立复核签收 verified ⇒ 两个槽位同时真空 "
                    "+ `advance.py --json` 实跑 `internal: []` (三个总工名下零 open) ⇒ 队列对这两条线真断线★** · "
                    "★**本单 = 纯分析/作业包类 (零写板·零落表·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①★**"),
            "brief_file": e["id"] and ("state/dispatch_briefs/" + (
                "ISS-377_mech_connector_clearance_caliber.md" if e["id"] == "ISS-377"
                else "ISS-378_sw_debug_header_fw_impact.md")),
            "status_note": "★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则会挡住任何 job "
                            "给这两个 agent 再派活 ⇒ 零撞车窗口★",
        })
    tmp2 = DLOG + ".tmp_%d" % os.getpid()
    with open(tmp2, "w", encoding="utf-8") as f:
        yaml.safe_dump(ddoc, f, allow_unicode=True, sort_keys=False,
                       default_flow_style=False, width=100000)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp2, DLOG)
    print("★ dispatch_log 已追加 2 条 (备份 %s)" % bak2)

    # ---- 3 守恒校验: 台账条数 ----
    n = len(doc2.get("issues") or [])
    print("★ 台账总条数 = %d (开单前 %d)" % (n, len(doc.get("issues") or [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
