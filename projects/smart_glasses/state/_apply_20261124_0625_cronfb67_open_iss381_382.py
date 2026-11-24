#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261124_0625_cronfb67_open_iss381_382.py
================================================
cron fb67af40 (ARS45 队列自动派活) 的【开单 + 直接落 fixing】· ISS-381 (sw-lead) + ISS-382 (mech-lead)

★**为什么开这两个单 (★本机实读 + 实算 · 不抄任何 agent 报告★)★**:
  ★① `python3 state/advance.py --json` 实跑 (2026-11-24 06:2x) ⇒ ★**`internal: []`** (三个总工名下零 open)
  ★② 台账实读 (375 条) ⇒ hw-lead: fixing 1 (ISS-380·真在飞) / sw-lead: open 0 fixing 0 / mech-lead: open 0 fixing 0
  ★③ ★**sw-lead 的活 = main 于 2026-11-24 06:0x 签收 ISS-379 时登记的 need `iss379_q6_uart_rx_zero_copper`
       (to=sw-lead, 在 state/fragments/pm.yaml 里)** ⇒ 本单把它转成正式单
  ★④ ★**mech-lead 的活 = main 于 2026-11-24 06:0x~06:1x 在 webchat 会话里独立复核出来的实测定论**
       (官方 SMD 排针变体实测 = 2 列 × 4 行, 而 ISS-371 已签收真相页写的是 "2x2 staggered";
        且该页自带的 G5 闸只判「有没有写交错」不判维数 ⇒ 真实盲区) ⇒ 本单把它转成正式单
  ★⑤ ★**本机实测出的一条【反向事实】写进 ISS-381 的 brief**: main need 里「unc 45→0 抓不到 UART_RX」这半句
       ★**被实测证伪** —— `UART_RX` 现在就是 45 条 unconnected 里的一条 (零铜 pad≥2 的网必然贡献 ≥1 条 unc item)
       ⇒ 真洞不是「unc 看不见它」, 而是「unc 是一条【计数】, 证明不了【是哪 23 条必需网被接上了】」
       ⇒ 验收线必须升级成【逐条列铜】⇒ 这正是 ISS-381 的正题

★**纪律 (★铁律⑩-i★)**: ★**先落 `fixing` 再 spawn** ⇒ ★**兄弟 job 775d9893 的 `advance.py --json` 看不见本条
  ⇒ 撞车窗口 = 0** ★
★**边界**: ★**零写板 · 零落表 · 零改既有闸 · 零改已签收件 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍
  ⇒ 不自签台账** ⇒ ★**纯分析 / 作业包类 (不动板)** ⇒ 合「板只改一次」纪律 ① ★

★**并发写盘护栏 (★照抄 ISS-380 那趟的做法★)**: `state/issue_log.yaml` 是 4.7 MB 大文件, main 的 webchat
  会话可能在同时刻写它 ⇒ ★**本脚本在 `os.replace` 之前重算一遍当前文件的 md5, 与开读时的 md5 比对
  ⇒ 不一致就中止 (rc=3) 让本 job 重跑** ★
"""
import hashlib
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state", "issue_log.yaml")
DLOG = os.path.join(PROJ, "state", "dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF_381 = "state/dispatch_briefs/ISS-381_sw_zero_false_connectivity_gate.md"
BRIEF_382 = "state/dispatch_briefs/ISS-382_mech_jdebug_arrangement_truth.md"

TITLE_381 = ("★★[★新主线·PCB 线·SW 侧·「板那一趟」] 布线验收线之【零假连通】自检闸: "
             "每条必需网按预期拓扑逐条列铜 (★纯分析+新建闸+沙盒预演·零写板) ★★")
DESC_381 = (
    "★**题 (来源 = main 2026-11-24 06:0x 登记的 need `iss379_q6_uart_rx_zero_copper`, to=sw-lead)★**: "
    "★**「板那一趟」的布线验收线目前只有一条 —— `unconnected 45 → 0`** ⇒ ★**那是一条【计数】, 不是【身份】** ⇒ "
    "★**它证明不了「是哪 23 条必需网被接上了」·★更证明不了「没被删网 / 没被标 NC 就蒙过去了」** ⇒ "
    "★**本单把验收线升级成【逐条列铜】: 每条必需网都必须单独证明自己真接上了** ★ "
    "★**★本机实测出的一条【反向事实】(★main need 里那半句被证伪★)★**: "
    "★**「unc 45→0 抓不到 UART_RX」不成立** —— `UART_RX` 现在就是 45 条 unconnected 里的一条 "
    "(DRC JSON `unconnected_items` 逐条读: 45 条 items / 43 个网名 · UART_RX → 1 项 · FSIN_OUT 1 · JTAG_TDI 1 · "
    "LED_G_D 1 · CAM_RESET_N 1 · USB_CC2 1 · SPI_*_BOOT 各 1 · 15 条差分腿各 1~2) ⇒ "
    "★**零铜 pad≥2 的网【必然】贡献 ≥1 条 unc item ⇒ 真洞是【计数 ≠ 身份】, 不是「unc 看不见它」** ⇒ "
    "★**三种刷法都能把 45 刷到 0 而一条铜都不加: ① 删网/删焊盘 ② 标 NC/no-connect ③ 改名/拆网** ⇒ "
    "★**⇒ 本单交一个 fail-closed 的逐条列铜自检闸 + 一页真相 + 订正块草稿 (★含证伪块·★老字一个字不许删★)** ★ "
    "★**边界 (★不许越界★)**: ① 「必需网零铜 ⇒ 必拒」**已经有人管了** (`HW/check_board_comparable_gate.py` L419/L429 名单层 "
    "+ `state/compare_arm_official.py` L114/L121) ⇒ **不许重做** ⇒ 本单落点是【身份/逐条/焊盘集合/可被计数刷掉】这四层 · "
    "② `HW/check_s8_target_list.py` 每次都 return 0 (只出尺子, 从不判红) ⇒ 全仓【没有】独立的「必需网逐条列铜」fail-closed 判据 ⇒ "
    "本单新建的那道就是第一个 · ③ `SW/tools/check_sw_zero_copper_grade_consistency.py` (C0~C9) 管的是【SW 页文字 vs 分级名单】"
    "(文档层), **不查板面铜** ⇒ 不重复 · ④ 差分腿铜长对称性阈值 main 尚未裁 ⇒ **只登记不代拍** ★ "
    "★**类别**: ★**纯分析 + 新建机器闸 + 沙盒预演 (零写板·零落表·零外发·不代拍)** ⇒ 合「板只改一次」纪律 ① ★"
)

TITLE_382 = ("★★[★新主线·PCB 线·MECH 侧·纯分析+新建闸·零写板] `J_DEBUG` 已签收真相页的 `2x2` 排布标签与实测矛盾 "
             "(★实测是 2 列 × 4 行★) + 对应闸 `G5` 只查「有没有写交错」不查维数 (★真实盲区★) ★★")
DESC_382 = (
    "★**题 (来源 = main 2026-11-24 06:0x~06:1x 在 webchat 会话里独立复核出来的实测定论)★**: "
    "★**官方 SMD 排针变体实测 = 2 列 × 4 行 (`2x4_staggered`)**, 而 ISS-371 已签收真相页 "
    "`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` L391 机器块写的是 `\"arrangement\": \"2x2 staggered\"` · "
    "正文 L45/L203/L207/L288/L471/L719 多处写「2 列 × 2 行交错」⇒ ★**同一页自己的 §3 表 (L208) 又写着"
    "「4 个焊盘在 Y 向排 4 行 (中心 ±0.635 / ±1.905)」⇒ 同一页自相矛盾**★ "
    "★**★而该页自带的闸 `MECH/check_jdebug_1p27_clearance.py` 的 `G5` (L576~L618) 才是真盲区: 它自己算出的是 "
    "`2x4_staggered` (★对的·L268~L275★), 但它只判页面 `arrangement` 字符串里【含】`staggered`/`交错` (L589~L591) "
    "⇒ ★**从不把页面声明的维数与自己实测的维数对比 ⇒ 页面写 `2x2` 照样绿、写 `9x9` 也照样绿**★★ "
    "★**页里钉的 `.kicad_mod` md5 锚 (THT `7a5f470c…` / SMD `9d6b0e63…`) 与盘上现值一致 ⇒ 标签是从一开始就写错的, "
    "不是库件变了的陈旧锚** ★ "
    "★**★错的是【标签 / 维数】, 不是【几何数字】—— 降级方案的铜箔包络 `6.0000 × 4.4600` 是按「X 向 2 列 (中心距 3.00) + "
    "「Y 向 4 行 (中心 ±0.635 / ±1.905)」算出来的 ⇒ 数字本身与 `2x4` 相容 ⇒ 订正块里必须把"
    "「① 标签维数写错」与「② 降级方案数值结论不因此改变」这两件分开写, 不许写成「结论错」**★ "
    "★**为什么现在要修 (★「板只改一次」纪律★)**: 错标签若不修, 「板那一趟」照着它选降级方案 ⇒ 板改第二次 ⇒ 违「板只改一次」 ★ "
    "★**边界 (★不许越界★)**: ★**已签收件 `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 与 "
    "`MECH/check_jdebug_1p27_clearance.py` 一个字节都不许动** ⇒ ★**本单只交【新页 + 新闸 + 订正块草稿】, 由 main 裁怎么落** "
    "(★先例 ISS-374 cont2 在已签收页上追加后 `MECH/check_connector_clearance_caliber.py` 的 `K7` 立刻红 2 条 ⇒ "
    "★**不要在已签收件上再制造一处**★) ★ "
    "★**类别**: ★**纯分析 + 新建机器闸 + 沙盒预演 (零写板·零落表·零改已签收件·零外发·不代拍)** ⇒ 合「板只改一次」纪律 ① ★"
)

NOTE_COMMON = (
    "★2026-11-24 06:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
    "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★ "
    "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
    "(三个总工名下零 open 可派) ② 台账实读 ⇒ sw-lead / mech-lead 均 open 0 / fixing 0 (hw-lead 的 ISS-380 真在飞, 不碰) "
    "③ ★**兄弟 job 775d9893 于 05:45 那轮撞出来的机制级发现: 26 条「已登记但从未开成单」的 need 悬在半空 ⇒ "
    "「needs → 单」这一步没人做 ⇒ 队列永远显示为空, 而活其实堆着** ★ "
    "④ ★**本轮同时给两份 brief 跑了命令存在性守卫 `state/check_brief_commands.py --brief-file` ⇒ 两份 rc=0** ★ "
    "★**外发口径 (硬约束)**: ★**不许外发任何邮件/询价/问询/采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ "
    "厂商资料一律【自己上网查】+ 标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) + 查不到就写降级方案 "
    "(降级方案是必须项) ★ "
    "★**边界**: 零写板 · 零落表 · 零改既有闸 · 零改已签收件 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍 · "
    "不自签 `state/issue_log.yaml` · 不写别人的分片 · 沙盒只落 `tmp/iss38X_sbx/` + `logs/iss38X/` (★**不许写系统 `/tmp`** ★) ★"
)

ISSUES = [
    {"id": "ISS-381", "title": TITLE_381, "severity": "high", "source_blocker": "ISS-379",
     "source_agent": "main", "desc": DESC_381, "owner": "sw-lead", "verify_by": "main",
     "reporter": "main", "raised": "2026-11-24", "due": "2026-11-27", "status": "fixing",
     "external": False, "need_keys": ["iss379_q6_uart_rx_zero_copper"],
     "task_brief": open(os.path.join(PROJ, BRIEF_381), encoding="utf-8").read(),
     "note": NOTE_COMMON + " ★ **任务书全文**: `" + BRIEF_381 + "` ★"},
    {"id": "ISS-382", "title": TITLE_382, "severity": "high", "source_blocker": "ISS-371",
     "source_agent": "main", "desc": DESC_382, "owner": "mech-lead", "verify_by": "main",
     "reporter": "main", "raised": "2026-11-24", "due": "2026-11-27", "status": "fixing",
     "external": False, "need_keys": ["iss371_arrangement_label_2x2_vs_2x4", "iss371_g5_dimension_blind_spot"],
     "task_brief": open(os.path.join(PROJ, BRIEF_382), encoding="utf-8").read(),
     "note": NOTE_COMMON + " ★ **任务书全文**: `" + BRIEF_382 + "` ★"},
]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_entry(e):
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
    for e in ISSUES:
        if e["id"] in ids:
            print("★★%s 已存在 ⇒ 停下, 不重复开单" % e["id"])
            return 2
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    bak = LOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw.rstrip("\n") + "\n")
        for e in ISSUES:
            f.write(dump_entry(e))
        f.flush()
        os.fsync(f.fileno())

    md5_now = md5(LOG)
    if md5_now != md5_before:
        os.unlink(tmp)
        print("★★中止 (rc=3): issue_log 在本脚本开读之后被改过 (md5 %s → %s) ⇒ 不写, 请重跑"
              % (md5_before, md5_now))
        return 3
    os.replace(tmp, LOG)

    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    got = {i.get("id"): i.get("status") for i in (doc2.get("issues") or [])}
    for e in ISSUES:
        assert got.get(e["id"]) == "fixing", (e["id"], got.get(e["id"]))
    assert len(doc2.get("issues") or []) == len(issues) + len(ISSUES), "条数不符"
    for i in issues:
        assert i.get("id") in got, "旧条目丢失: %s" % i.get("id")
    print("★ issue_log 已落: ISS-381=fixing / ISS-382=fixing (条数 %d → %d · 备份 %s · 新 md5=%s)"
          % (len(issues), len(doc2.get("issues") or []), os.path.basename(bak), md5(LOG)))

    ddoc = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert isinstance(ddoc, list)
    bak2 = DLOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(DLOG, bak2)
    for e in ISSUES:
        ddoc.append({
            "issue": e["id"], "agent": e["owner"], "at": "2026-11-24",
            "brief": e["title"], "brief_file": BRIEF_381 if e["id"] == "ISS-381" else BRIEF_382,
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 06:2x · ★**开单 + 直接落 fixing + spawn** "
                    "(★铁律⑩-i 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) · "
                    "★**开单依据 = advance.py --json 实跑 internal: [] + 台账实读 sw-lead/mech-lead 均 open 0 fixing 0 "
                    "+ 兄弟 job 775d9893 05:45 撞出的机制级发现「needs → 单 这一步没人做」★** · "
                    "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★ · "
                    "★**纯分析 / 作业包类 (零写板·零落表·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★"),
            "status_note": "★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则会挡住任何 job 再派活 ⇒ 零撞车窗口★",
        })
    tmp2 = DLOG + ".tmp_%d" % os.getpid()
    with open(tmp2, "w", encoding="utf-8") as f:
        yaml.safe_dump(ddoc, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100000)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp2, DLOG)
    d2 = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert isinstance(d2, list) and d2[-1]["issue"] == "ISS-382"
    print("★ dispatch_log 已追加: ISS-381 + ISS-382 (条数 %d → %d · 备份 %s)"
          % (len(ddoc) - 2, len(d2), os.path.basename(bak2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
