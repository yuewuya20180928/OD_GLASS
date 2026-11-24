#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261124_0615_cronfb67_open_iss380.py
==============================================
main (项目总工) 的【开单 + 落 fixing】· ISS-380 (hw-lead)
「板那一趟」`J_DEBUG` / `J_UART` 座体【厂商具体型号 + 座体真实高度 + 厂商 keepout 图纸】官网自查证

★**为什么开这个单 (★本机实读 + 实算 · 不抄任何 agent 报告★)**:
  ★① `python3 state/advance.py --json` 实跑 (2026-11-24 06:1x) ⇒ ★**`internal: []`** (三个总工名下零 open 可派)
  ★② 台账 `state/issue_log.yaml` 实读 (374 条) ⇒ ★**hw-lead open 0 / fixing 0** (★`ISS-379` 已于 05:5x 被 main
     独立复核签收 `verified`★) ⇒ ★**hw-lead 槽位真空 + 名下零 open 项 ⇒ 不补新单则槽位空转** ★
  ★③ ★**兄弟 job 775d9893 05:45 那轮的机制级发现**: 26 条「已登记但从未开成单」的 need 悬在半空
     ⇒ 「needs → 单」这一步没人做 ⇒ 队列永远显示为空, 而活其实堆着 ★
  ★④ ★**本轮为什么不派 OI-3 (落点认不认)**: main 2026-11-24 06:0x 已裁 ISS-379 §6② ⇒ 三个候选坐标全部挂在
     现役板 160×100 的框上, 而「板只改一次」画甲还是乙的【上位问题】还没答 ⇒ 派 OI-3 = 派一个前置未落的空活 ★
  ★⑤ ★**OI-10 (厂商型号 / keepout 图纸) 不受上位问题影响** ⇒ 与 `iss267_mech_debug_part_model` 的第①③条合并成一单 ★

★**纪律 (★铁律⑩-i★)**: ★**先落 `fixing` 再 spawn** ⇒ ★**兄弟 job 775d9893 的 `advance.py --json` 看不见本条
  ⇒ 撞车窗口 = 0** ★
★**边界**: ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍 · 不自签台账**
  ⇒ ★**纯分析 / 作业包类 (不动板)** ⇒ 合「板只改一次」纪律 ① ★

★**并发写盘护栏 (★main 2026-11-24 06:1x 加★)**: `state/issue_log.yaml` 是 4.7 MB 大文件, 且 main 的 webchat
  会话此刻正在写它 (历史上已发生过「同路径写盘被吞」一次 ⇒ ISS-370 CONT2 B7-3)
  ⇒ ★**本脚本在 `os.replace` 之前重算一遍当前文件的 md5, 与开读时的 md5 比对 ⇒ 不一致就中止 (rc=3) 让你重跑** ★
"""
import hashlib
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
DLOG = os.path.join(PROJ, "state/dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")
BRIEF = "state/dispatch_briefs/ISS-380_hw_debug_uart_seat_part_truth.md"

TITLE = ("★★[★新主线·PCB 线·HW 侧·「板那一趟」] `J_DEBUG` / `J_UART` 座体的【厂商具体型号 + 座体真实高度 + "
         "厂商 keepout 图纸】官网自查证 (★OI-10 + iss267 第①③条合并·纯分析/作业包类·零写板) ★★")

DESC = (
    "★**题 (来源 = mech-lead 交回的两条 need, 不是本 job 造的口径)★**: ① `iss377_oi10_vendor_part_numbers` "
    "(to=hw-lead): 「J_DEBUG / J_UART 用哪颗具体厂商型号? J_SOM_P1..P4 与 J_USB_C 的厂商 keepout 图纸从哪里补? "
    "本单零外发只登记」 ② `iss267_mech_debug_part_model` (to=hw-lead) 的第①条 (板侧 `J_DEBUG` 脚数真值 = 1×4) "
    "与第③条 (座体真实高度 = `[0数据]`)。 ★ "
    "★**main 本机实读 (2026-11-24 06:1x·只读真板 + 只读 BOM/脚表·可复跑)★**: `HW/BOM_v1.csv:71` = `J_DEBUG,1,1×4 1.27mm "
    "排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,待定,,待定,待定,连接器,型号/间距/引脚编号待结构与装配复核 (★本版 pin "
    "编号自拟)` ⇒ **厂商型号 = 「待定」**; `HW/BOM_v1.csv:77` = `J_UART,1,1×2 1.27mm 排针 (UART),…,待定,…`; "
    "`HW/netlist_v1_pins.csv:202`~`205` = `J_DEBUG.pin1..4` → `JTAG_TCK`/`JTAG_TMS`/`JTAG_TDI`/`JTAG_TDO` (★脚编号自拟★); "
    "`HW/netlist_v1_pins.csv:275`~`276` = `J_UART.pin1/pin2` → `UART_TX`/`UART_RX`; 现役板框 160×100 ⇒ **本单不碰任何坐标** "
    "(坐标挂上位问题); 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` "
    "⇒ 19 天逐字节未动 ★ "
    "★**本单要交四件**: ① 真相页 `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` (§0 一句话结论 · §1 板侧真值 · "
    "§2 厂商型号候选表 (各 ≥2 个具体料号 + 证据等级 + URL) · §3 座体真实高度 (查不到 ⇒ `[0数据]` + 降级方案) · "
    "§4 keepout/机械图纸来源登记 (`J_SOM_P1`~`P4` + `J_USB_C` 逐个一行) · §5 与结构侧模型的三条不自洽点 (只登记·不改结构侧的文件) · "
    "§6 未决项 (只登记不代拍) · §7 复跑命令) ② 新闸 `HW/check_debug_uart_seat_truth.py` (K0~K5 · 每条反向用例 · "
    "`--selftest` 末行 `ALL TESTS PASS` · ★**零挂链★**) ③ 交卷页 (B1~B6 六段, 六个 `##` 标题必须命中 gate_check 关键词) "
    "④ `hw.yaml` 分片登记 (只走 `state/frag_write.py`) ★"
)

NOTE = (
    "★2026-11-24 06:1x~06:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
    "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★ "
    "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
    "(三个总工名下零 open 可派 ⇒ 队列对 HW 这条线真断线) ② 台账实读 374 条 ⇒ hw-lead open 0 / fixing 0 "
    "(★`ISS-379` 已于 2026-11-24 05:5x 由 main 独立复核签收 `verified`★) ③ ★**兄弟 job 775d9893 于 05:45 那轮撞出来的"
    "机制级发现: 26 条「已登记但从未开成单」的 need 悬在半空 ⇒ 「needs → 单」这一步没人做 ⇒ 队列永远显示为空, 而活其实堆着★ "
    "④ ★**本轮明确不派 OI-3 (落点认不认)**: main 2026-11-24 06:0x 已裁 ISS-379 §6② ⇒ 三个候选坐标全部挂在现役板 160×100 的框上, "
    "而「板只改一次」画甲(台架板)还是乙(产品内板)的【上位问题】还没答 ⇒ 若乙则三个坐标全部作废 ⇒ 派 OI-3 = 派一个前置未落的空活★ "
    "⑤ ★**OI-10 不受上位问题影响** (型号/高度/图纸与板框无关) ⇒ 与 `iss267_mech_debug_part_model` 第①③条合并成一单★ "
    "★**类别**: ★**纯分析 / 作业包类** (★老板 2026-11-17 00:43: 目标是绘制 PCB 图 ⇒ PCB 线可派, 但板只改一次 ⇒ 先派不动板的★) ★ "
    "★**外发口径 (硬约束)**: ★**不许外发任何邮件/询价/问询/采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ 厂商资料"
    "一律【自己上网查】+ 标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) + 查不到就写降级方案 (降级方案是必须项) ★ "
    "★**边界**: 零写板 · 零落表 (★不许改 BOM / 网表 / 脚表 / 板 / 原理图★) · 零改既有闸 · 零改既有页面正文 "
    "(★只许新建 4 件★) · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml` · 不写别人的分片 (★`mech.yaml` 那两条 need "
    "是 mech-lead 的地界★) · 沙盒只落 `tmp/iss380/` + `logs/iss380/` ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-380_hw_debug_uart_seat_part_truth.md` "
    "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★"
)

ISSUE = {
    "id": "ISS-380",
    "title": TITLE,
    "severity": "high",
    "source_blocker": "ISS-377",
    "source_agent": "main",
    "desc": DESC,
    "owner": "hw-lead",
    "verify_by": "main",
    "reporter": "main",
    "raised": "2026-11-24",
    "due": "2026-11-26",
    "status": "fixing",
    "external": False,
    "need_keys": ["iss377_oi10_vendor_part_numbers", "iss267_mech_debug_part_model"],
    "task_brief": open(os.path.join(PROJ, BRIEF), encoding="utf-8").read(),
    "note": NOTE,
    "dispatched_at": "2026-11-24",
}


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_entry(e):
    """★把一条 issue 序列化成 YAML 列表项 (0 缩进 '- id:' + 2 缩进字段)★"""
    txt = yaml.safe_dump({"issues": [e]}, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=100000)
    lines = txt.split("\n")
    assert lines[0].startswith("issues:"), lines[0]
    return "\n".join(lines[1:]).rstrip("\n") + "\n"


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    if ISSUE["id"] in ids:
        print("★★%s 已存在 ⇒ 停下, 不重复开单" % ISSUE["id"])
        return 2
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    # ---- 1 先落 issue_log (status=fixing, 铁律⑩-i) ----
    bak = LOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw.rstrip("\n") + "\n" + dump_entry(ISSUE))
        f.flush()
        os.fsync(f.fileno())

    # ★★并发写盘护栏: replace 之前重算 md5 ⇒ 别人在我读之后写过 ⇒ 中止 (★宁可这一轮不派, 也不吞掉别人的写★)
    md5_now = md5(LOG)
    if md5_now != md5_before:
        os.unlink(tmp)
        print("★★中止 (rc=3): issue_log 在本脚本开读之后被改过 (md5 %s → %s) ⇒ 不写, 请重跑"
              % (md5_before, md5_now))
        return 3
    os.replace(tmp, LOG)

    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    got = {i.get("id"): i.get("status") for i in (doc2.get("issues") or [])}
    assert got.get("ISS-380") == "fixing", got.get("ISS-380")
    assert len(doc2.get("issues") or []) == len(issues) + 1, "条数不符"
    for i in issues:  # ★旧条目一条不许少 (★防吞页★)
        assert i.get("id") in got, "旧条目丢失: %s" % i.get("id")
    print("★ issue_log 已落: ISS-380=fixing (条数 %d → %d · 备份 %s · 新 md5=%s)"
          % (len(issues), len(doc2.get("issues") or []), os.path.basename(bak), md5(LOG)))

    # ---- 2 再落 dispatch_log (追加式) ----
    ddoc = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert isinstance(ddoc, list)
    bak2 = DLOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(DLOG, bak2)
    ddoc.append({
        "issue": "ISS-380",
        "agent": "hw-lead",
        "at": "2026-11-24",
        "brief": TITLE,
        "brief_file": BRIEF,
        "job": ("cron fb67af40 (ARS45 队列自动派活) · ★本 job 步骤 2 的动作: ★**开单 + 直接落 fixing + spawn** "
                "(★铁律⑩-i 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) · "
                "★**开单依据 = `advance.py --json` 实跑 `internal: []` (三个总工名下零 open) + `ISS-379` 已于 05:5x 被 main "
                "签收 verified ⇒ hw-lead 槽位真空 ⇒ 队列对 HW 这条线真断线★** · "
                "★**本单 = mech-lead 交回的 need `iss377_oi10_vendor_part_numbers` + `iss267_mech_debug_part_model` 的第①③条 "
                "合并成一条正式单 (OI-10 不受【板框上位问题】影响, 而 OI-3 受影响 ⇒ OI-3 本轮不派)★** · "
                "★**纯分析/作业包类 (零写板·零落表·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①★**"),
        "status_note": "★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则会挡住任何 job 给 hw-lead "
                        "再派活 ⇒ 零撞车窗口★",
    })
    tmp2 = DLOG + ".tmp_%d" % os.getpid()
    with open(tmp2, "w", encoding="utf-8") as f:
        yaml.safe_dump(ddoc, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100000)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp2, DLOG)
    d2 = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert isinstance(d2, list) and d2[-1]["issue"] == "ISS-380"
    print("★ dispatch_log 已追加: ISS-380 (条数 %d → %d · 备份 %s)" % (len(ddoc) - 1, len(d2), os.path.basename(bak2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
