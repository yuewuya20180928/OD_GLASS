#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-19 00:1x · 新开 ISS-335 (sw-lead) + ISS-336 (mech-lead) 并直接派出** ★

★**为什么新开 (★逐条本机实读·不抄任何 agent 报告★)**:
  ① `python3 state/advance.py --json` ⇒ ★**`internal: []`** ⇒ 三个总工名下 **零 `open` 零 `fixing`** ⇒ ★**队列真空 ⇒ 不开单就断线** ★
  ② `sessions_list` ⇒ ★**hw-lead 有一条【活会话】在跑 (★`agent:hw-lead:subagent:3e83935f…` · status=running · startedAt 1795017540761 ⇒ 00:0x 才起·★它就是上一轮本 job 派出去的 ISS-334★) ⇒ ★**本轮【不碰 hw-lead】****
  ③ sw-lead / mech-lead ⇒ ★**两条最近会话全是 done / timeout (★无活会话★) ⇒ 可派** ★
  ④ ★**派活前置闸**: `python3 state/check_brief_commands.py --brief-file …` ⇒ ★**两份 brief 都 rc=0** ★

★**本轮派的两条 (★都是「板只改一次」主线上的【真缺口】·★都不是凑数★)**:
  ★**ISS-335 (sw-lead)** = ★★「板只改一次」那一趟的【SW 侧准出汇总闸】★★
    · ★**病灶**: ★**MECH 侧有 `MECH/check_onepass_mech_release.py` (ISS-300 已交卷) ⇒ ★**SW 侧【零个】对标物** (★`ls SW/tools/` 零个 release/准出/summary 闸★) ⇒ ★★「SW 侧能不能出 Gerber」今天在 SW 域【没有任何机器答案】★★
    · ★**本机实读**: ★**16 道 `SW/tools/check_*.py` 裸跑【全绿】(★TMPDIR 指项目内·★本 job 00:0x 逐个实跑★) ⇒ ★【绿不是问题】·★【没有汇总闸才是问题】★★
    · ★**★关键事实**: ★**ISS-321 实测的「板那一趟当天必跑 10 道闸」里, 有 4 道【不在 `state/gate_check.py` 链上】(★`check_demo_panel_spec.py` / `check_shutdown_semantics.py` / `check_timing_review_adc_sync.py` / `timing_check.py` ⇒ ★本机 `grep -c` 逐个实读 = 0★) ⇒ ★**汇总闸必须把它们收进去, 否则当天红了没人知道**★★
    · ★**另两条已实测的接线事实**: ★**三道 R6 selftest 闸【必须裸跑】(★argparse 里没有 `--selftest` ⇒ 带了就 rc=2 usage 错误★) ★+ ★**TMPDIR 必须指项目内 (★本机 `/tmp` 配额已到顶 ⇒ EDQUOT 假红★)** ★
    · ★**边界**: ★**零写板 · 零落表 · 零改既有 16 道闸 · 零改 `state/gate_check.py`** (★挂链是 main 的机制地界★) ★
  ★**ISS-336 (mech-lead)** = ★★「板只改一次」那一趟的【板框冻结闸 U-1 机器闸实现】★★
    · ★**病灶**: ★**ISS-316 已把判据【设计稿】全出好 (★`MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` §2 的 C1~C7 L167~L173 + RC-1~RC-6 L182~L187★) ★+ ★**main 已于 2026-11-18 09:4x 把决策码 M-B18 的 (a) 项裁成【路 B = 做成机器闸】★★ ⇒ ★★**裁都裁了, 闸却一直没建** ⇒ ★★`ls MECH/check_board_frame_freeze_gate.py` ⇒ 【不存在】★★**
    · ★**后果 (ISS-319 §D-2-1 逐字)**: ★**「闸 `proto_pcb_freeze_gate` 永远不满足 ⇒ 板那一趟没有第一前置 ⇒ S1~S8 可在 U-1 未拍时开工 ⇒ 板 md5 第二次变 ⇒ Gerber/投产包/留证链全部作废重做 = 2-4 周 + ¥4-8K」★★**
    · ★**★本单挖出的一个真缺陷 (★已写进 brief·★不是抄文档★)**: ★**ISS-316 §2 的 C7 写「读 `state/issue_log.yaml` 的闭合记录」⇒ ★★本机实读 `state/issue_log.yaml` 顶层只有 `_schema` / `_owners_legal` / `issues` 三项, 【零条 need 闭合记录】⇒ ★★C7 真正该读的是【分片侧】的 `needs_closed` (★64 条★) 与 `answers` (★79 条★) ⇒ ★★这正是 ISS-281 §3-S10 那一类「判据引用了盘上不存在的字段」的病 ⇒ 本单必须实测纠正并显式登记★★**
    · ★**边界**: ★**零写板 · 零落表 · 零改既有 MECH/*.py · 零改 `state/gate_check.py` · 不许代老板拍 U-1 · 不许造假的闭合记录让闸变绿** ★

★**纪律**: ★**status 直接落 `fixing` ⇒ 无 `open` 窗口 ⇒ 下一轮 in_flight 规则会跳过这两个 agent ⇒ 兄弟 job 775d9893 不会重复派** ★
★**零写板 · 零落表 · 零改既有闸 · 零改 agent 分片 · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·本 job 自己也不发★)**
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
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-19 00:1x"
STAMP = "20261119_0015_cronfb67_open335_336"

BRIEF_335 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-335_sw_release_summary_gate.md"),
    encoding="utf-8",
).read()
BRIEF_336 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-336_mech_board_frame_freeze_gate.md"),
    encoding="utf-8",
).read()

TITLE_335 = (
    "★★[★新主线·PCB 线·纯新建闸类·内部活] ★★"
    "**「板只改一次」那一趟的【SW 侧准出汇总闸】** "
    "(★对标 MECH 侧 ISS-300 的 `MECH/check_onepass_mech_release.py` · "
    "★SW 侧【零个】对标物 ⇒ 「SW 侧能不能出 Gerber」今天在 SW 域【没有任何机器答案】★) "
    "★★ ⇒ ★**本单 = ① SW 侧 10 道必跑闸的清单页 (★ISS-321 实测表 + 链外 4 道★) "
    "② fail-closed 汇总闸本体 (★脚本不存在/跑不起来/超时/rc≠0 ⇒ 一律汇总红 + 清单完备性★) "
    "③ 反向用例 (★沙盒副本·真件零碰★) ④ 板那一趟当天 SW 侧的逐字 SOP "
    "⑤ 给 main 的一行挂链写法 (★本单自己不改 `state/gate_check.py`★) "
    "★【纯新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改 gate_check.py】★★"
)

DESC_335 = (
    "MECH 侧 ISS-300 已交卷 `MECH/check_onepass_mech_release.py` (21,227 B) ⇒ 一条命令给出「结构侧能不能出 Gerber」"
    "⇒ fail-closed (脚本不存在/跑不起来/超时 ⇒ 一律闸红) + 清单完备性检查 (6 道里有 1 道不在清单里 ⇒ 汇总红) + "
    "`--selftest` 反向用例 (沙盒副本跑, 真件一个字节不碰)。"
    "★SW 侧本机实读【零个】对标物★ (`ls SW/tools/` ⇒ 零个 release/准出/summary 闸; `ls SW/` ⇒ 44 个文件里零个汇总闸) "
    "⇒ 「SW 侧能不能出 Gerber」这个问题今天在 SW 域没有任何机器答案。"
    "★★更具体的后果★: 「板只改一次」那一趟当天, SW 侧必跑闸漏跑一条 ⇒ 没人知道 ⇒ "
    "要么先签收 (假绿流到下一趟) 要么收工验收时才炸 (现场只剩两条路: 当场返工改板 ⇒ 板 md5 变第二次 ⇒ 整趟白跑; "
    "或先签收再说 ⇒ 假绿流到下一趟)。"
    "★而且板那一趟当天板 md5 会【合法地】变一次 ⇒ 若 SW 侧有钉板 md5 闸当天必然从绿转红 ⇒ "
    "现场最容易误读成「板改坏了」→ 去改板凑绿 → 板 md5 变第二次 → 整趟白跑。"
    "★本机实读 (2026-11-19 00:0x, 16 道裸跑, TMPDIR 指项目内)★: 16/16 全 rc=0 ⇒ 【绿不是问题】·【没有汇总闸才是问题】。"
    "★关键事实★: ISS-321 实测的「板那一趟当天必跑 10 道闸」里有 4 道【不在 state/gate_check.py 链上】"
    "(check_demo_panel_spec.py / check_shutdown_semantics.py / check_timing_review_adc_sync.py / timing_check.py ⇒ "
    "本机 grep -c 逐个实读 = 0) ⇒ 汇总闸必须收进去, 否则当天红了没人知道。"
    "★另两条已实测的接线事实★: 三道 R6 selftest 闸【必须裸跑】(argparse 里没有 --selftest ⇒ 带了就 rc=2 usage 错误) + "
    "TMPDIR 必须指项目内 (本机 /tmp 带 usrquota 且配额已到顶 ⇒ 沙盒写 /tmp ⇒ OSError 122 ⇒ 6 道闸一起假红)。"
    "⇒ 本单只出【纯新建闸 + 作业包】, 一个字节都不许写板。"
)

TITLE_336 = (
    "★★[★新主线·PCB 线·纯新建闸类·内部活] ★★"
    "**「板只改一次」那一趟的【板框冻结闸 U-1 机器闸实现】** "
    "(★ISS-316 §2 已把 C1~C7 七条判据 + RC-1~RC-6 六条反向用例的设计稿全部出好 · "
    "★main 已于 2026-11-18 09:4x 把决策码 M-B18 的 (a) 项裁成【路 B = 做成机器闸】 · "
    "★但 `MECH/check_board_frame_freeze_gate.py` 至今【不存在】⇒ 裁了不做 = 裁了跟没裁一样★) "
    "★★ ⇒ ★**本单 = ① 冻结闸本体 (★C1~C7 逐条照设计稿实现 · 阈值一律只读 "
    "`MECH/service_port_check.py` + `MECH/board_frame_feasibility.py` + `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:FRAMES`★) "
    "② 六条反向用例 + 一条正向对照 (★沙盒副本·真件零碰★) "
    "③ ★★C7 真源的实测纠正 (★ISS-316 §2 写「读 issue_log」⇒ ★★本机实读 issue_log 顶层零条 need 闭合记录 ⇒ "
    "★真源是【分片侧】`needs_closed` (64 条) + `answers` (79 条)·★这正是 ISS-281 §3-S10 那一类「判据引用了盘上不存在的字段」的病★) "
    "④ 一页说明 + 交卷页 + 「U-1 拍完之后这闸怎么变绿」的落表格式说明 "
    "★【纯新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改 gate_check.py · 不代老板拍 U-1】★★"
)

DESC_336 = (
    "ISS-316 (verified) 已把板框冻结闸的判据【设计稿】全部出好: "
    "`MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` §2 的 C1~C7 七条判据 (L167~L173) + RC-1~RC-6 六条反向用例 (L182~L187), "
    "阈值一律只读 `MECH/service_port_check.py` 与 `MECH/board_frame_feasibility.py` 的现值。"
    "★main 已于 2026-11-18 09:4x 把决策码 M-B18 的 (a) 项裁成【路 B = 做成机器闸】(DECISION_INDEX_2026-11-18.md §E-1 第 2 行) "
    "⇒ 但本机实读 `ls MECH/check_board_frame_freeze_gate.py` ⇒ 【不存在】⇒ 全仓 grep 该闸名 ⇒ 只在 "
    "`MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` / ISS-319 交卷单 / 决策页 / 台账里作为「待建的闸」被引用, 没有文件本体。"
    "★★后果 (ISS-319 §D-2-1 逐字)★★: 「闸 proto_pcb_freeze_gate 永远不满足 ⇒ 板那一趟没有第一前置; "
    "HW 作业包硬顺序首行是「网表」而不是「板框冻结」⇒ S1~S8 可在 U-1 未拍时开工 ⇒ 板 md5 第二次变 ⇒ "
    "Gerber / 投产包 / 留证链全部作废重做 = 2-4 周 + ¥4-8K」。"
    "★本机实读 (2026-11-19 00:0x)★: `MECH/board_frame_feasibility.py` 的 all_rows() ⇒ 36 档 (12/12/12 三套框), "
    "字段含 frame_id / layers / thk / can_open / red_reasons / holes / cavity / margins / weight_g; "
    "`HW/PCB/BOARD_FRAME_CALIBER.md` 的 cal:FRAMES ⇒ current_frame = B160x100 (三套 id = B160x100 / F30A / P60x15); "
    "`MECH/service_port_check.py` ⇒ BASE / TOL={fdm_part:0.30, fdm_feat:0.25} / CRIT = 2*TOL = 0.60mm; "
    "`state/fragments/mech.yaml` ⇒ needs_from 里有 key=proto_pcb_freeze_gate (to=main, since=2026-10-29, due=2026-10-31) "
    "⇒ 这条 need 还没闭合 ⇒ C7 今天必然红 (那是如实报告病灶, 不是闸坏了)。"
    "★★本单挖出的一个真缺陷 (已写进 brief, 不是抄文档)★★: ISS-316 §2 的 C7 写「读 state/issue_log.yaml 的闭合记录」"
    "⇒ 但本机实读 issue_log 顶层只有 _schema / _owners_legal / issues 三项, 零条 need 闭合记录 "
    "⇒ C7 真正该读的是【分片侧】的 needs_closed (64 条) 与 answers (79 条) "
    "⇒ 这正是 ISS-281 §3-S10 那一类「判据引用了盘上不存在的字段」的病 ⇒ 本单必须实测纠正并显式登记, 不许悄悄改。"
    "⇒ 本单只出【纯新建闸 + 作业包】, 一个字节都不许写板。"
)

SUMMARY_335 = (
    "★★**新开单 + 直接派出 (status 直接落 fixing ⇒ 无 open 窗口 ⇒ 下一轮 in_flight 会跳过 sw-lead ⇒ 兄弟 job 775d9893 不会重复派)** ★ ★"
    "★**开单依据 (★2026-11-19 00:1x 本机实读★)**: "
    "★**① `python3 state/advance.py --json` ⇒ `internal: []`** ⇒ 三个总工名下零 open 零 fixing ⇒ 队列真空 ⇒ 不开单就断线 ★ "
    "★**② sw-lead 最近会话全 done/timeout (无活会话) ⇒ 可派** ★ "
    "★**③ 病灶 = SW 侧【零个】准出汇总闸** (`ls SW/tools/` ⇒ 零个 release/准出/summary; `ls SW/` 44 个文件里零个) ⇒ "
    "MECH 侧有 ISS-300 的 `MECH/check_onepass_mech_release.py` 对标物而 SW 侧没有 ⇒ 「SW 侧能不能出 Gerber」无机器答案 ★ "
    "★**④ 16 道 SW 单闸裸跑全绿 (TMPDIR 指项目内) ⇒ 绿不是问题, 没汇总闸才是问题** ★ "
    "★**⑤ ISS-321 那 10 道必跑闸里有 4 道不在 `state/gate_check.py` 链上** (grep -c 逐个实读 = 0: "
    "`check_demo_panel_spec.py` / `check_shutdown_semantics.py` / `check_timing_review_adc_sync.py` / `timing_check.py`) ⇒ "
    "汇总闸必须收进去, 否则当天红了没人知道 ★ "
    "★**⑥ 三道 R6 selftest 闸必须裸跑 (argparse 无 --selftest ⇒ 带了就 rc=2 usage 错误) + TMPDIR 必须指项目内 (本机 /tmp 配额到顶 ⇒ EDQUOT 假红)** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-335_sw_release_summary_gate.md` (10,765 B · `check_brief_commands.py --brief-file` rc=0) ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · "
    "零改既有 16 道 `SW/tools/check_*.py` (只读调用) · 零改 `state/gate_check.py` (挂链归 main) · 零改既有 `SW/*.md` 正文 · "
    "零改 `HW/` 与 `MECH/` 任何文件 · 零改 `state/issue_log.yaml` · 零改 pm/hw/mech 三份分片 · 沙盒只写 `tmp/iss335/` + `logs/iss335/` · "
    "不替老板拍板 · 不替 main 拍机制地界的活 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log ★"
)

SUMMARY_336 = (
    "★★**新开单 + 直接派出 (status 直接落 fixing ⇒ 无 open 窗口 ⇒ 下一轮 in_flight 会跳过 mech-lead ⇒ 兄弟 job 775d9893 不会重复派)** ★ ★"
    "★**开单依据 (★2026-11-19 00:1x 本机实读★)**: "
    "★**① `python3 state/advance.py --json` ⇒ `internal: []`** ⇒ 三个总工名下零 open 零 fixing ⇒ 队列真空 ⇒ 不开单就断线 ★ "
    "★**② mech-lead 最近会话全 done/timeout (无活会话) ⇒ 可派** ★ "
    "★**③ 病灶 = 板框冻结闸【判据设计稿已在盘 (ISS-316 §2 C1~C7 + RC-1~RC-6) + main 已裁路 B (M-B18 的 (a) 项) · "
    "但 `MECH/check_board_frame_freeze_gate.py` 本机实读【不存在】⇒ 裁了不做 = 裁了跟没裁一样】** ★ "
    "★**④ 后果 (ISS-319 §D-2-1 逐字)**: 「闸 proto_pcb_freeze_gate 永远不满足 ⇒ 板那一趟没有第一前置 ⇒ "
    "S1~S8 可在 U-1 未拍时开工 ⇒ 板 md5 第二次变 ⇒ Gerber/投产包/留证链全部作废重做 = 2-4 周 + ¥4-8K」 ★ "
    "★**⑤ ★★本单挖出的一个真缺陷 (★不是抄文档★)★★: ISS-316 §2 的 C7 写「读 `state/issue_log.yaml` 的闭合记录」⇒ "
    "★本机实读 issue_log 顶层只有 _schema/_owners_legal/issues 三项、零条 need 闭合记录 ⇒ ★真源是【分片侧】的 "
    "`needs_closed` (64 条) + `answers` (79 条) ⇒ ★★这正是 ISS-281 §3-S10 那一类「判据引用了盘上不存在的字段」的病 ⇒ "
    "本单必须实测纠正并显式登记, 不许悄悄改** ★ "
    "★**⑥ 36 档矩阵本机可跑 (all_rows() = 36) + cal:FRAMES 的 current_frame = B160x100 + service_port_check 的 CRIT = 0.60mm ⇒ 阈值全部只读得到** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-336_mech_board_frame_freeze_gate.md` (9,000 B · `check_brief_commands.py --brief-file` rc=0) ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · "
    "零改既有 `MECH/*.py` (service_port_check / board_frame_feasibility / check_board_frame_coords / check_onepass_mech_release 只读) · "
    "零改 `state/gate_check.py` (挂链归 main) · 零改既有 `MECH/*.md` 与 `HW/**/*.md` 正文 · 零改 `HW/` 任何文件 · "
    "零改 `state/issue_log.yaml` · 零改 pm/sw/hw 三份分片 · 沙盒只写 `tmp/iss336/` + `logs/iss336/` · "
    "★★不代老板拍 U-1 · 不许造假的闭合记录让闸变绿 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log ★"
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
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        new_specs = (
            ("ISS-335", "sw-lead", TITLE_335, DESC_335, BRIEF_335, SUMMARY_335),
            ("ISS-336", "mech-lead", TITLE_336, DESC_336, BRIEF_336, SUMMARY_336),
        )
        for iid, owner, title, desc, brief, _summary in new_specs:
            if iid in idx:
                # 幂等: 已存在 ⇒ 只兜底 status=fixing + 补 brief
                it = idx[iid]
                if it.get("status") != "fixing":
                    it["status"] = "fixing"
                    applied.append("%s status → fixing (★兜底·幂等★)" % iid)
                continue
            issues.append({
                "id": iid,
                "title": title,
                "severity": "high",
                "source_blocker": "ISS-334",
                "source_agent": "main",
                "desc": desc,
                "owner": owner,
                "reporter": "main",
                "raised": "2026-11-19",
                "due": "2026-11-20",
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "task_brief": brief,
                "note": (
                    "★2026-11-19 00:1x cron fb67af40 新开并直接派出 (status 落 fixing ⇒ "
                    "下一轮 in_flight 规则会跳过该 agent ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)★ "
                    "★**依据**: 队列排空 (advance.py internal=[]) + 三个总工名下零 open 零 fixing "
                    "(hw-lead 名下 ISS-334 有活会话在跑 ⇒ 本轮不碰) + 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」"
                    "⇒ PCB 线可派 + 「板只改一次」铁律 ⇒ 只派纯新建闸/作业包类 (★零写板·零落表·零改既有闸·零改 gate_check.py★)★ "
                    "★**任务书全文**: `state/dispatch_briefs/%s` (★`check_brief_commands.py --brief-file` rc=0★)★"
                    % (
                        "ISS-335_sw_release_summary_gate.md" if iid == "ISS-335"
                        else "ISS-336_mech_board_frame_freeze_gate.md"
                    )
                ),
                "dispatched_at": "2026-11-19",
            })
            applied.append("新开 %s (%s) · status 直接落 fixing" % (iid, owner))

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or {}
        entries = dlog.get("dispatches") or []
        for iid, owner, _t, _d, _b, summary in new_specs:
            if not any(e.get("issue") == iid for e in entries):
                entries.append({
                    "issue": iid,
                    "agent": owner,
                    "at": "2026-11-19",
                    "brief": summary,
                    "job": (
                        "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-19 00:1x · "
                        "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                    ),
                })
                applied.append("dispatch_log.yaml += %s %s 1 条" % (iid, owner))

        atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=10**6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
