#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261124_0715_cronfb67_cont1_381_382_open_383.py
==========================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-24 07:1x
★**ISS-381 cont1 (sw-lead) · ISS-382 cont1 (mech-lead) · 新开 ISS-383 (hw-lead)★**

★**本轮动作 (本机实读 + 实算 · 不抄任何 agent 报告)★**:
  ★① `python3 state/advance.py --json` 实跑 ⇒ `internal: []` (三个总工名下零 open 可派)
  ★② 台账实读 (377 条) ⇒ hw-lead fixing 1 (ISS-380) / sw-lead fixing 1 (ISS-381) / mech-lead fixing 1 (ISS-382)
  ★③ ★**会话实况 (sessions_list + 盘上 transcript mtime 双向核对)★**:
      - ISS-380 (hw-lead) 会话 `e4a6efff…` ⇒ `status=done` · endedAt 06:18:11 ⇒ ★**已交卷** (真相页 + 闸 + 交卷页 + hw.yaml 分片四件都在盘) ⇒ ★**签收归 main, 本 job 不签** ⇒ ★**hw-lead 槽位真空**
      - ISS-381 (sw-lead) 会话 `fb908701…` ⇒ `status=timeout` + `abortedLastRun=true` · endedAt 06:56:17 · runtimeMs 737,696 (≈12.3 分钟) ⇒ ★**掐死** · ★**四件交付物零落盘** ⇒ ★**必须续派 cont1**
      - ISS-382 (mech-lead) 会话 `166fef77…` ⇒ `status=timeout` + `abortedLastRun=true` · endedAt 06:56:16 · runtimeMs 716,511 (≈12.0 分钟) ⇒ ★**掐死** · ★**闸已在盘 (`MECH/check_jdebug_arrangement_truth.py` 53,040 B @06:51) 但真相页/交卷页/分片零落盘** ⇒ ★**必须续派 cont1**
  ★④ ★**死因同型 (项目硬规矩 L-13 / L-18)★**: 两趟都是「重活 + 交付物放同一趟」⇒ 攒了一堆读数在上下文里 ⇒ 墙一到 ⇒ 什么都没留下 ⇒ ★**本轮 cont1 一律改成【落盘趟】(读数已在盘·不许重跑·先落盘再继续)** ★
  ★⑤ ★**ISS-383 的来源 = ISS-380 交卷时自查出的新不自洽 (板面 0.5mm SMD 占位盘 / BOM「1.27mm 直插排针」/ 结构侧 Cortex-10 2×5 ⇒ 三方三个口径)⇒ 没有任何人负责把它们对起来** ★

★**纪律 (★铁律⑩-i★)**: ★**先落 `fixing` 再 spawn** ⇒ ★**兄弟 job 775d9893 的 `advance.py --json` 看不见 ⇒ 撞车窗口 = 0** ★
★**边界**: ★**零写板 · 零落表 · 零改既有闸 · 零改已签收件 · 零挂链 · 零外发 · 不代拍 · 不自签台账** ⇒ ★**纯分析 / 作业包类** ⇒ 合「板只改一次」纪律 ① ★
★**并发写盘护栏**: `state/issue_log.yaml` 是 4.8 MB 大文件, main 的 webchat 会话可能同时刻写它 ⇒ ★**本脚本在 `os.replace` 之前重算 md5, 与开读时不一致就中止 (rc=3)** ★
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

BRIEF_381_C = "state/dispatch_briefs/ISS-381_sw_zero_false_connectivity_gate_cont1.md"
BRIEF_382_C = "state/dispatch_briefs/ISS-382_mech_jdebug_arrangement_truth_cont1.md"
BRIEF_383 = "state/dispatch_briefs/ISS-383_hw_debug_uart_seat_alignment.md"

# ------------------------------------------------------------------ ISS-383
TITLE_383 = ("★★[★新主线·PCB 线·HW 侧·纯分析+新建闸·零写板] 座体选型的【四方对齐作业包】: "
             "候选件真实规格 / 库封装可得性 / BOM 型号栏草案 / 三方口径闸 ★★")

DESC_383 = (
    "★**题 (来源 = ISS-380 交卷时自查出的新不自洽, 不是本 job 造的口径)★**: "
    "★**`J_DEBUG` / `J_UART` 这两行 BOM 现在有【四个口径】而它们互相矛盾, 而没有人负责把它们对起来★** ⇒ "
    "① **BOM 描述栏** (`HW/BOM_v1.csv:71` / `:77`) = 「1×4 / 1×2 1.27mm 排针」⇒ 单排 · 直插 · 1.27 mm (★型号栏仍「待定」★) · "
    "② **板面实际封装** = 两个都是 **0.5 mm 排距 SMD 占位盘** (`J_DEBUG` 4 pad @`(144.3000, 58.0000)` · "
    "`J_UART` 2 pad @`(18.6400, 68.6000)`/`(19.1400, 68.6000)`) ⇒ ★**既不是 1.27 也不是直插** · "
    "③ **结构侧模型** = Cortex-10 2×5 (`jd_cols=5` `jd_rows=2` · 必须清空区 X `7.62`) ⇒ 脚数与排布都不同 · "
    "④ **E-1 板决策** = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` + "
    "`HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` §2.1 第③行 ⇒ land pitch `0.50 → 1.27` 要在【同一趟】做完 ★ "
    "★**ISS-380 已把首选候选登记好 (`J_DEBUG` = Samtec `FTSH-104-01-F-DV` · `J_UART` = Samtec `FTSH-102-01-F-DV`, "
    "均 1.27mm 直插 THT 垂直), 但 §2 里「单排 1×4 / 1×2 的排布」只到家族页, 官网单品页二次确认只标 `[推算]` ⇒ "
    "★**真实排布与 pin 方径仍未坐实★** ⇒ ★**而且本地库里 `Connector_PinHeader_1.27mm.pretty` 的 "
    "`PinHeader_1x0N_P1.27mm_Vertical` 是【沿局部 Y 一列 N 个】(THT 单排) 而 `_SMD_Pin1Left/Right` 是【2 列 × N 行交错】⇒ "
    "★「1×4」这个脚数在库里对应【两种排布】⇒ 选错封装 = 针序全变 = 插反 = 救砖链不通★** ★ "
    "★**本单要交四件**: ① 真相页 `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md` "
    "(§0 一句话结论 · §1 候选件真实规格表 (★只深挖 D-1/U-1 两个首选件·其余 6 个各一行状态·查不到标 `[0数据]` + 降级方案★) · "
    "§2 库封装可得性表 (★逐个解析 `.kicad_mod`·不许只抄库名·不许拿「排距一样」当「封装可用」★) · §3 四方口径对齐表 · "
    "§4 BOM 型号栏草案 (★只给草案·★不落表★) · §5 未决项 · §6 复跑命令) "
    "② 新闸 `HW/check_debug_uart_seat_alignment.py` (K0~K4 · 每条反向用例 · `--selftest` 末行 `ALL TESTS PASS` · ★**零挂链★**) "
    "③ 交卷页 (B1~B6 六段, 六个 `##` 标题必须命中 gate_check 关键词) ④ `hw.yaml` 分片登记 (只走 `state/frag_write.py`) ★ "
    "★**不重复谁**: ★**落位几何 = ISS-376 / ISS-379 已 verified ⇒ 不许重做** · ★**针序契约 = ISS-375 已交卷 "
    "(`SW/tools/check_debug_pin_order_contract.py`) ⇒ 不许重做** · ★**料号清单本体 = ISS-380 (★只读·不改★)** · "
    "★**MECH 侧排布标签 = ISS-382 (mech-lead 在飞) ⇒ 不许碰 MECH 的文件** ★ "
    "★**★不许把任何一个口径【改掉】去迁就另一个★ (★项目硬规矩 L-15: 「几份各自正确的数对不上」是「板只改一次」那一趟最贵的风险★) "
    "⇒ 只允许【登记差异 + 各自会引发什么 + 给代价】⇒ 裁决归 main + mech-lead** ★ "
    "★**类别**: ★**纯分析 + 新建机器闸 + 库清单核对 (零写板·零落表·零外发·不代拍)** ⇒ 合「板只改一次」纪律 ① ★"
)

NOTE_383 = (
    "★2026-11-24 07:1x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
    "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★ "
    "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
    "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ hw-lead `fixing 1` (`ISS-380`) · 但 ★**该会话 `e4a6efff…` "
    "`status=done` · endedAt 06:18:11 ⇒ 已交卷 (真相页 + 闸 + 交卷页 + `hw.yaml` 分片四件都在盘) ⇒ 签收归 main, "
    "本 job 不签 ⇒ hw-lead 槽位真空** ③ ★**上游 = ISS-380 交卷页 §2 (首选件排布只到家族页, 官网单品页二次确认标 `[推算]`) "
    "+ §5-④ (板面封装 / BOM 描述 / 结构侧模型 三方三个口径) ⇒ 本单就是把它落成可执行作业包 + 一道对齐闸** ★ "
    "④ ★**命令存在性守卫 `state/check_brief_commands.py --brief-file state/dispatch_briefs/"
    "ISS-383_hw_debug_uart_seat_alignment.md` ⇒ rc=0** ★ "
    "★**外发口径 (硬约束)**: ★**不许外发任何邮件/询价/问询/采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ "
    "厂商资料一律【自己上网查】+ 标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) + 查不到就写降级方案 "
    "(降级方案是必须项) ★ "
    "★**边界**: 零写板 · 零落表 · 零改既有闸 · 零改已签收件 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml` · "
    "不写别人的分片 · 沙盒只落 `tmp/iss383_sbx/` + `logs/iss383/` (★**不许写系统 `/tmp`** ★) ★ "
    "★ **任务书全文**: `" + BRIEF_383 + "` ★"
)

# -------------------------------------------------- ISS-381 / ISS-382 cont1
NOTE_381_ADD = (
    "★2026-11-24 07:1x cron fb67af40 【cont1 续派 (★不是重做·★)】★★ ★**死因 (本机实读)★**: "
    "上一子会话 `agent:sw-lead:subagent:b55663b5-2cc8-4f58-9e22-00e692911b66` "
    "(sessionId `fb908701-f453-48d6-babb-7035b69be1ac`) 于 06:56:17 【掐死】(★`status=timeout` + "
    "`abortedLastRun=true` + startedAt 06:43:57 + runtimeMs 737,696 ≈ 12.3 分钟·★transcript 571,250 B @06:56 "
    "在盘·★不是空壳·★有 tool_use 记录★)★ ⇒ ★**四件交付物零落盘** (`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` 无 · "
    "`SW/tools/check_sw_false_connectivity_gate.py` 无 · 交卷页 无 · `state/fragments/sw.yaml` 里 `iss381` 命中 0) ★ "
    "⇒ ★**死因 = 重活与交付物放同一趟 (12 分钟全花在读资料 + 跑探针上·最后一步才开始写) ⇒ 墙一到 ⇒ 什么都没留下 "
    "(★项目硬规矩 L-13 的第二种形态★)** ★ ★**但上一趟的重活【已经在盘】★**: `tmp/iss381_sbx/probe_pads.py` (自写 s-expr 解析器) · "
    "`tmp/iss381_sbx/board_nets.json` (43,364 B · 每网 `cu` 铜长 mm / `seg` 铜段数 / `pads` 焊盘集合) · "
    "`tmp/iss381_sbx/board_nets_pcbnew.json` (25,867 B · pcbnew 口径对照) · `tmp/iss381_sbx/probe_pcbnew.py` · "
    "`logs/iss381/baseline_fingerprints.txt` (板 + 三张表 + 5 个既有闸 + 1 个既有页的 md5 基线) ⇒ "
    "★**cont1 = 落盘趟: 读数已在盘·不许重跑·第一个动作就是写交付物·每完成一件立刻落盘** ★ "
    "★**续做任务书全文**: `" + BRIEF_381_C + "` (★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**status 保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py 看不见 ⇒ 撞车窗口 0★) ★"
)

NOTE_382_ADD = (
    "★2026-11-24 07:1x cron fb67af40 【cont1 续派 (★不是重做·★)】★★ ★**死因 (本机实读)★**: "
    "上一子会话 `agent:mech-lead:subagent:0fa8bb52-63c9-44f2-ae07-472831cac2f0` "
    "(sessionId `166fef77-ac5b-46f1-8eb2-115f121a9b5b`) 于 06:56:16 【掐死】(★`status=timeout` + "
    "`abortedLastRun=true` + startedAt 06:44:18 + runtimeMs 716,511 ≈ 12.0 分钟·★transcript 497,757 B @06:56 在盘★)★ ⇒ "
    "★**真相页 / 交卷页 / 分片三件零落盘** ⇒ ★**但闸本体已在盘**: `MECH/check_jdebug_arrangement_truth.py` "
    "(53,040 B @06:51) ⇒ ★**main 本机实跑 `python3 MECH/check_jdebug_arrangement_truth.py --selftest` ⇒ 报 "
    "`✗ 正向对照直接 IO 失败: 文件不在盘: …/MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` ⇒ ★★【闸本身没坏·只差页】★★ "
    "⇒ ★**cont1 = 收尾趟: 闸就是页的规格书 ⇒ 读它 → 照它写页 → 闸立刻就绿** ★ "
    "★**另一份重活也已在盘**: `tmp/iss382_sbx/ledger.json` (1,554 B · 已签收页里全部「几列×几行 / 2x2 / 2×2」表述的逐处清单 "
    "file/line/surface/cols/rows/staggered/proposed) · `tmp/iss382_sbx/gen_ledger.py` · `tmp/iss382_sbx/probe_claims.py` / "
    "`probe_claims2.py` · `logs/iss382/before_check_connector_caliber.log` (★K7 本来就红 2 条·★是基线不是要修的★) · "
    "`logs/iss382/before_check_jdebug_1p27.log` ⇒ ★**不许重扫整页** ★ "
    "★**续做任务书全文**: `" + BRIEF_382_C + "` (★命令存在性守卫 rc=0★) ★ "
    "★**status 保持 fixing 不动** (★铁律⑩-k①★) ★"
)


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


def dump_field(name, value):
    txt = yaml.safe_dump({name: value}, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=100000)
    lines = txt.split("\n")
    return "\n".join(l for l in lines[1:] if l.strip()) + "\n"


def insert_field(raw, issue_id, field, value):
    """在 issue_log 原文里, 给指定 issue 条目【追加】一个字段 (追加式·老字一字未删)"""
    lines = raw.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("- id: %s" % issue_id):
            start = i
            break
    if start is None:
        raise SystemExit("★★找不到条目 %s" % issue_id)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("- id: "):
            end = j
            break
    # 去掉条目尾部空行
    k = end
    while k > start + 1 and lines[k - 1].strip() == "":
        k -= 1
    add = dump_field(field, value).rstrip("\n").split("\n")
    return "\n".join(lines[:k] + add + lines[k:]) + "\n"


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    if "ISS-383" in ids:
        print("★★ISS-383 已存在 ⇒ 停下, 不重复开单")
        return 2
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    # --- ① ISS-381 / ISS-382 追加 note_addendum (status 保持 fixing) ---
    raw2 = insert_field(raw, "ISS-381", "note_addendum", NOTE_381_ADD)
    raw2 = insert_field(raw2, "ISS-382", "note_addendum", NOTE_382_ADD)

    # --- ② 新开 ISS-383 (直接落 fixing) ---
    e383 = {
        "id": "ISS-383", "title": TITLE_383, "severity": "high", "source_blocker": "ISS-380",
        "source_agent": "main", "desc": DESC_383, "owner": "hw-lead", "verify_by": "main",
        "reporter": "main", "raised": "2026-11-24", "due": "2026-11-27", "status": "fixing",
        "external": False, "need_keys": ["iss380_seat_arrangement_truth", "iss380_three_caliber_mismatch"],
        "task_brief": open(os.path.join(PROJ, BRIEF_383), encoding="utf-8").read(),
        "note": NOTE_383,
    }
    raw2 = raw2.rstrip("\n") + "\n" + dump_entry(e383)

    bak = LOG + ".bak_%s_cronfb67_open383" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw2)
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
    assert got.get("ISS-383") == "fixing", ("ISS-383", got.get("ISS-383"))
    assert got.get("ISS-381") == "fixing" and got.get("ISS-382") == "fixing"
    assert len(doc2.get("issues") or []) == len(issues) + 1, "条数不符"
    for i in issues:
        assert got.get(i.get("id")) == i.get("status"), ("status 被改", i.get("id"))
    for i in doc2.get("issues") or []:
        if i.get("id") in ("ISS-381", "ISS-382"):
            assert i.get("note_addendum"), "%s 缺 note_addendum" % i.get("id")
    print("★ issue_log 已落: ISS-381/382 追加 note_addendum (status 仍 fixing) + 新开 ISS-383=fixing "
          "(条数 %d → %d · 备份 %s · 新 md5=%s)"
          % (len(issues), len(doc2.get("issues") or []), os.path.basename(bak), md5(LOG)))

    # --- ③ dispatch_log 追加三条 ---
    ddoc = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert isinstance(ddoc, list)
    bak2 = DLOG + ".bak_%s_cronfb67_open383" % STAMP
    shutil.copy2(DLOG, bak2)
    JOB = ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 07:1x · ★**%s** · "
           "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★ · "
           "★**纯分析 / 作业包类 (零写板·零落表·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★")
    ddoc.append({
        "issue": "ISS-381", "agent": "sw-lead", "at": "2026-11-24",
        "brief": "★★[cont1 续派] 布线验收线之【零假连通】自检闸: 每条必需网按预期拓扑逐条列铜 · ★**落盘趟**",
        "brief_file": BRIEF_381_C,
        "job": JOB % ("cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 06:56:17 掐死·★12.3 分钟零交付·★读数已在盘·★不许重跑★)"),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
    })
    ddoc.append({
        "issue": "ISS-382", "agent": "mech-lead", "at": "2026-11-24",
        "brief": "★★[cont1 续派] `J_DEBUG` 排布标签订正页 + `G5` 维数盲区新闸 · ★**收尾趟 (闸已在盘·只差页)★",
        "brief_file": BRIEF_382_C,
        "job": JOB % ("cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 06:56:16 掐死·★闸已在盘 `MECH/check_jdebug_arrangement_truth.py`·★只差真相页/交卷页/分片★)"),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
    })
    ddoc.append({
        "issue": "ISS-383", "agent": "hw-lead", "at": "2026-11-24",
        "brief": TITLE_383,
        "brief_file": BRIEF_383,
        "job": JOB % ("新开 + 直接落 fixing (★铁律⑩-i 先落 fixing 再 spawn★) · ★**开单依据 = ISS-380 已交卷 (06:18 done) 留出的 hw-lead 槽位真空 + ISS-380 交卷页 §2/§5-④ 自查出的三方口径不自洽 ⇒ 本单落成可执行作业包 + 一道对齐闸★)"),
        "status_note": "★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则会挡住任何 job 给 hw-lead 再派活 ⇒ 零撞车窗口★",
    })
    tmp2 = DLOG + ".tmp_%d" % os.getpid()
    with open(tmp2, "w", encoding="utf-8") as f:
        yaml.safe_dump(ddoc, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100000)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp2, DLOG)
    d2 = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert isinstance(d2, list) and d2[-1]["issue"] == "ISS-383"
    print("★ dispatch_log 已追加: ISS-381(cont1) + ISS-382(cont1) + ISS-383 (条数 %d → %d · 备份 %s)"
          % (len(ddoc) - 3, len(d2), os.path.basename(bak2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
