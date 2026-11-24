#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0920_cronfb67_open_387_388_389.py
==================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-24 09:2x
★**新开 3 条 + 直接落 fixing** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)

★**为什么现在要新开 (★本机实读·不抄任何 agent 报告★)**:
  ★① `python3 state/advance.py --json` ⇒ `internal: []` ⇒ 三个总工名下零 open 可派
  ★② ★**但三个槽位并不是真空, 是被【已交卷待签收】的 fixing 占着** ★
     (★ISS-384/385/386 三单: hw.yaml 08:55 / sw.yaml 08:54 / mech.yaml 08:57 均有本单登记·
      ★交卷页 08:56~08:58 三件在盘 · ★**三个 agent 的会话全部 status=done·无运行中会话**★)
     ⇒ ★**这三个槽位一签收就立刻空出来 ⇒ 本 job 必须【趁 main 签收前】把下一批活落到位** ★
  ★③ ★**三条 need 至今没人答** (★本机逐 key 实读 fragments★):
     · `iss383_main_single_row_1x27_vendor_pn` (to=main · ★**main 08:3x 自己改写了 A2 建议,
       ★但同一行明文要求「铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认」★ ⇒ ★**这条自己开的口子没人补**★)
     · `iss379_q4_mech_opening_and_clearance` (to=mech-lead · ★**main 明令「两连接器合到一件答」★)
     · ★**★本 job 本轮实测新发现的真病灶 (不在 need 表里)★**: ★**两道【已签收 verified】的 SW 闸今天实测真的 FAIL** ★
       (★`SW/tools/check_debug_pin_order_contract.py --selftest` = 10/11 FAIL · ★默认 TMPDIR=/tmp ⇒ 沙盒 ROOT 退成 `/`★)
       (★`SW/tools/check_sw_board_md5_rebase_readiness.py --selftest` = 0/10 FAIL · ★闸裸跑 5/7 rc=1★)
       ★⇒ **两道闸都【零挂链】⇒ daily_check/gate_check 全绿 ⇒ 没人看见 ⇒ 本 job 本轮把它变成可判的** ★
  ★④ ★**三条都【不碰板】** ⇒ 合「板只改一次」纪律 ① (先派不动板的)

★**并发写盘护栏**: `state/issue_log.yaml` 是 4.8 MB 大文件, main 的 webchat 会话此刻【正在签收 ISS-384/385/386】
  ⇒ ★**本脚本在 `os.replace` 之前重算 md5, 与开读时不一致就中止 (rc=3)** ★

★**边界**: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板
          · 不改别人分片 · 只写 issue_log.yaml + dispatch_log.yaml + 本脚本自身
"""
import hashlib
import os
import shutil
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF_387 = "state/dispatch_briefs/ISS-387_hw_fts_single_row_land_truth.md"
BRIEF_388 = "state/dispatch_briefs/ISS-388_sw_gate_failure_diagnosis.md"
BRIEF_389 = "state/dispatch_briefs/ISS-389_mech_debug_seat_rework_spec.md"

JOB = ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 09:2x · "
       "★**新开 + 直接落 fixing (★铁律⑩-i 先落 fixing 再 spawn★) · "
       "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` 三条全 rc=0** ★ · "
       "★**纯分析 / 作业包 / 新建闸类 (零写板·零落表·零改既有闸·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★ · "
       "★**开单依据 = 三个槽位被【已交卷待签收】的 fixing 占着 + 三条 need 没人答 + 本 job 实测新发现两道签收闸真的坏了** ★")


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


NOTE_TAIL = ("★**台账 status 直接落 fixing (★不是 open★) ⇒ advance.py 的 in_flight 规则会挡住任何 job "
             "给该 agent 再派活 ⇒ 零撞车窗口★**")

BOUND = ("★**本单性质**: 纯分析 + 作业包 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · "
         "零外发 · 不代拍 ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★\n"
         "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file <brief>` rc=0** ★\n")


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    for iid in ("ISS-387", "ISS-388", "ISS-389"):
        if iid in ids:
            print("★★%s 已存在 ⇒ 停下, 不重复开单" % iid)
            return 2
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    def brief(p):
        return open(os.path.join(PROJ, p), encoding="utf-8").read()

    # ---------------- ISS-387 · hw-lead ----------------
    e387 = {
        "id": "ISS-387",
        "title": ("★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建闸·零写板] 「板只改一次」那一趟的 "
                  "`J_DEBUG`/`J_UART` 单排直插【原厂 land 几何】官网查证 + 与盘上通用封装逐项对比 + "
                  "对 MECH 3D 判据链的传感到影响面 ★★"),
        "severity": "high",
        "source_blocker": "ISS-383",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建文档/闸·零写板·零落表]★\n\n"
                 "★**题 (来源 = `DECISION_ONE_PAGER_2026-11-22.md` §㊳ 的 **发现二** + 同段 **A2** 行★)★: ★\n\n"
                 "★**① main 2026-11-24 08:3x 签收 ISS-383 时独立复核推翻了 ISS-383 §0-2「两家的 1.27mm 都没有单排」** ⇒ "
                 "★**Samtec 【FTS】系列有单排直插 1.27mm**: `FTS-104-01-F-S` (4 位 1 排 直插) / `FTS-102-01-F-S` (2 位 1 排 直插) "
                 "(★Mouser + DigiKey 参数表双源 + Samtec 官网 FTS 家族页「FTS - .050\" (1,27mm) Low Profile, "
                 ".016\" (.41mm) Square Post Terminal Strip, **Single Row**」★) ⇒ ★**板侧真值档 (1×4 单排直插) 有现成可采购件** ★\n\n"
                 "★**② 但同一条 §㊳ A2 自己写了三个不许跳过的字**: ★**「但铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认 "
                 "(★FTS 的 post 是 .016″ (.41mm) 方柱, 与 FTSH 的 .41 mm 不同族, **不许拿 FTSH 的铜箔数顶替**)」** ⇒ "
                 "★**⇒【料号】main 已拍; 【land 几何】官方明文要求官网单品页二次确认 ⇒ 至今 0 人做** ★\n\n"
                 "★**③ main 本机实读: `FTS-104-01-F-S` 在 HW/ MECH/ SW 三域页面里命中 0 次** ⇒ "
                 "★**全项目没有任何一页写下了 FTS 单排件的官方 land 几何** ★\n\n"
                 "★**★④ 后果比「少一页文档」严重 (★本单最要紧的一条★)★**: ★**MECH 侧那一整条 3D 判决链的铜箔宽, "
                 "读的是【通用 KiCad 库件】, 不是【那颗 FTS 厂件】** ★ ⇒ `MECH/check_debug_seat_3d_fit.py` L98~L101 (★main 实读★): "
                 "`KICAD_LIB = \".../Connector_PinHeader_1.27mm.pretty\"` + `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` / "
                 "`PinHeader_1x02_P1.27mm_Vertical.kicad_mod` ⇒ ★**那两颗件的铜箔宽 `4.8100` / `2.2700` 就是 MECH 全部 3D 余量数的输入** ★ ⇒ "
                 "★**⇒ 若 FTS 原厂 land 的铜箔宽 ≠ 通用件 ⇒ MECH 的 `6.6100` / `4.0700` / `2.6950` / `0.1350` 全线要重算** ⇒ "
                 "★**★★⇒ 这就是「板只改一次」那一趟最该先钉死的那一个数: 铜箔宽一变, 结构件出件口径整个变** ★★★ ★\n\n"
                 "★**⑤ 本单地界 = 查【厂件官网/官网单品页/分销参数表】里的 land 几何** ⇒ ★**零外发** ★ "
                 "(★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ "
                 "★**查不到就写 `[0数据]` + 降级方案, 不许写「等原厂回信」** ★\n\n"
                 + BOUND),
        "owner": "hw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss383_main_single_row_1x27_vendor_pn", "iss377_oi10_vendor_part_numbers",
                      "iss382_jdebug_vendor_part"],
        "task_brief": brief(BRIEF_387),
        "note": ("★2026-11-24 09:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ hw-lead 名下 ISS-384 已交卷 (hw.yaml 08:55 有本单登记) "
                 "⇒ 槽位待 main 签收后释放 ⇒ 本 job 趁窗口期把下一批落到位 ③ ★**本单 trigger = §㊳ A2 自己开的口子 "
                 "(「铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认」+「不许拿 FTSH 的铜箔数顶替」) 至今 0 人补** "
                 "④ ★**main 本机实读 `MECH/check_debug_seat_3d_fit.py` L98~L101 ⇒ 3D 链的铜箔宽读的是通用 KiCad 库件 "
                 "⇒ 若 FTS 厂件 land 不同则 MECH 全链要重算** ★\n"
                 + BOUND
                 + NOTE_TAIL),
    }

    # ---------------- ISS-388 · sw-lead ----------------
    e388 = {
        "id": "ISS-388",
        "title": ("★★[★新主线·PCB 线·SW 侧·纯分析+新建闸·零写板] 两道【已签收 verified】的 SW 闸今天实测"
                  "【真的坏了】⇒ 把「闸的失效」本身变成可判的 (★判据与环境耦合 + 账本与现实漂移★) ★★"),
        "severity": "high",
        "source_blocker": "ISS-375",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·SW 侧·纯分析+新建闸·零写板·零落表]★\n\n"
                 "★**题 (来源 = ★**本 job 2026-11-24 09:1x 例行核验时本机实跑发现**·★不抄任何 agent 报告★)★: ★\n\n"
                 "★**★本 job 把 SW 域 12 道闸逐个 `--selftest` 跑了一遍 ⇒ ★**有两道【已经签收 verified】的闸今天实测真的 FAIL** ★★ "
                 "★★**而且两道都【零挂链】(`grep -c state/gate_check.py` = 0) ⇒ daily_check / gate_check 全绿 ⇒ 没人看见** ★★ ★\n\n"
                 "★**★闸 1 · `SW/tools/check_debug_pin_order_contract.py` (ISS-375 签收件) ⇒ `--selftest` 10/11 FAIL (rc=1)★★** ★\n"
                 "```\n"
                 "  [FAIL] M2  把 D2 的算式改成手算常数 (变异本闸源码)  期望红=D2,D4\n"
                 "         实红=FATAL: 变异体无 JSON 输出 · FATAL: [Errno 2] No such file or directory:\n"
                 "           '/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md'\n"
                 "=== selftest 10/11 PASS (共 11 条反向用例) ===  SELFTEST FAILED\n"
                 "```\n"
                 "★**main 本机已定位根因 (★不用重找, 但要独立复核★)**: ★**该闸 `ROOT` 从 `__file__` 往上退两级算出** (★L39★) ⇒ "
                 "★**M2 把闸源码复制到沙盒再跑 ⇒ 副本的 `ROOT` 跟着沙盒目录走 ⇒ 沙盒落 `/tmp` 时 `ROOT` 退成 `/` ⇒ "
                 "它去找 `/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` ⇒ 不存在 ⇒ FATAL** ★ ⇒ "
                 "★**main 本机实测对照 (★这就是「环境依赖」的直接证明★)**: "
                 "★`python3 … --selftest` ⇒ 10/11 FAIL (默认 TMPDIR=/tmp) · ★`TMPDIR=\"$PWD/tmp\" python3 … --selftest` ⇒ 11/11 PASS★ ⇒ "
                 "★★**⇒ 同一份代码同一块板, 换个环境就红 ⇒ 这条反向用例是【环境敏感】的不是【判据敏感】的 ⇒ 而它正是 ISS-375 签收时"
                 "【亲手加的】【变异本闸源码⇒证明闸真在读 KiCad 变换】那条命门用例** ★★ ★\n\n"
                 "★**★闸 2 · `SW/tools/check_sw_board_md5_rebase_readiness.py` (ISS-372 签收件) ⇒ 裸跑 5/7 rc=1 + `--selftest` 0/10 FAIL★★** ★\n"
                 "```\n"
                 "  [FAIL] H1 · §1 清单漏登记: SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23 / :201 /\n"
                 "         SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215 / SW/tools/check_sw_false_connectivity_gate.py:73\n"
                 "  [FAIL] H4 · SW/tools/check_sw_false_connectivity_gate.py 硬钉了板 md5 但没进 §2 的账\n"
                 "  闸结果 5/7 通过, rc=1\n"
                 "  --selftest ⇒ 反向用例: 0/10 通过 ⇒ 有用例 FAIL ⇒ 本闸不可信 ⇒ rc=1\n"
                 "```\n"
                 "★**main 本机实读出的根因**: ★**H1/H4 判红【不是闸坏了】, 是【账本没跟上】—— ★**ISS-381 新建的 "
                 "`check_sw_false_connectivity_gate.py` 硬钉了板 md5, 且 ISS-381/ISS-385 新建的页面里也有板 md5 字面量, "
                 "它们都没进 ISS-372 真相页的 §1/§2 账** ⇒ ⇒ ★**这两条判据本来就是干这个用的, 它们【抓对了】** ⇒ "
                 "★**真正的病灶是: 当 SW 域新增一道钉板 md5 的闸时, 没有任何机制提醒「§2 的账要跟着登记」⇒ 账与现实漂移 "
                 "⇒ 闸自己判红 ⇒ 而它【零挂链】⇒ 这条红没人看见 ⇒ 就这么烂在盘上** ★\n\n"
                 "★**★本单的一句话定位★**: ★**闸不是坏了, 是【判据与环境耦合】+【账本与现实漂移】⇒ ★**这两类失效【今天没人能看见】"
                 "(零挂链) ⇒ ★**本单把「闸的失效」本身变成可判的** ★★ ★\n\n"
                 "★**★为什么这两道闸烂掉要紧 (★「板只改一次」那一趟的护栏★)★**: ★**`check_debug_pin_order_contract` = 物理针序契约; "
                 "`check_sw_board_md5_rebase_readiness` = 板 md5 引用面自守 ⇒ ★**它们一旦烂掉, 那一趟就没有护栏**★ ★\n\n"
                 + BOUND),
        "owner": "sw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss370_cont2_existing_gate_drift", "iss381_cont1_gate_chain_mount"],
        "task_brief": brief(BRIEF_388),
        "note": ("★2026-11-24 09:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实跑·不抄任何 agent 报告)★**: ① `state/advance.py --json` ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ sw-lead 名下 ISS-385 已交卷 (sw.yaml 08:54 有本单登记) "
                 "⇒ 槽位待 main 签收后释放 ③ ★**★本 job 本轮实测新发现 (不在任何 need 表里)★: ★**两道【已签收 verified】的 SW 闸"
                 "今天实测真的 FAIL** ★ — `check_debug_pin_order_contract.py --selftest` = 10/11 (★默认 TMPDIR=/tmp ⇒ 沙盒 ROOT 退成 `/`★) "
                 "· `check_sw_board_md5_rebase_readiness.py --selftest` = 0/10 (★闸裸跑 5/7 rc=1·★H1/H4 是【账本没跟上】不是闸坏★) "
                 "⇒ ★**两道都零挂链 ⇒ daily_check/gate_check 全绿 ⇒ 没人看见** ★ ⇒ "
                 "★**⇒ 本单把这两类失效模式(判据与环境耦合 / 账本与现实漂移)变成可判的** ★\n"
                 "★**★两条已答 need 的关联**: `iss370_cont2_existing_gate_drift` (★既有闸由绿转红·★只登记不代裁★) 与本单同型; "
                 "`iss381_cont1_gate_chain_mount` (★新闸挂不挂链★) ⇒ ★**本单新闸同样零挂链, 挂链与否归 main 裁** ★\n"
                 + BOUND
                 + NOTE_TAIL),
    }

    # ---------------- ISS-389 · mech-lead ----------------
    e389 = {
        "id": "ISS-389",
        "title": ("★★[★新主线·PCB 线·MECH 侧·纯分析+作业包+新建闸·零写板] `J_DEBUG`/`J_UART` 两连接器的"
                  "【座体 / 开口 / 清空区 三件合到一件】的结构侧收口作业包 ★★"),
        "severity": "high",
        "source_blocker": "ISS-386",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·MECH 侧·纯分析+作业包+新建机器闸+沙盒预演·零写板·零落表]★\n\n"
                 "★**题 (来源 = `state/fragments/pm.yaml` 的 need `iss379_q4_mech_opening_and_clearance` · ★since 2026-11-24★)★: ★\n\n"
                 "★**① main 已明确下令: 这两件事必须【合到一件】答, 不许分两票★** ⇒ 原文: ★**「这一条与 J_DEBUG 侧 "
                 "(ISS-377 算出铜箔每边超清空区 `1.5175`) 是【同源问题】⇒ ★**建议 mech-lead 把两条【合到一件】答 "
                 "(一次给座体/开口/清空区的整体结论, 而不是分别给两个落点的结论) ⇒ ★**否则两个连接器的答案可能互相矛盾, "
                 "而两个连接器在【同一趟】里改 ⇒ 矛盾就得改第二次 ⇒ 违「板只改一次」**」★ ⇒ "
                 "★**时限 (main 硬要求): 「板那一趟」开工前必须答完 ⇒ 因为结构件一旦开模/下单就没法回头** ⇒ "
                 "★**⇒ 答复窗口 = 与板框上位问题 (`boss_u1_upper_axis_board_trip_physical_product`) 的答复窗口【同一个】** ★\n\n"
                 "★**② ISS-386 交卷后 8 条 OI 挂在 mech 分片上, 至今没人答 (★main 本机实读 `state/fragments/mech.yaml`★)★**: ★\n"
                 "★`iss386_oi5_jdebug_clearance_x_pick_one` (★清空区 X 宽三档 `1.7750`/`4.0850`/`4.8100` 选哪个★) · "
                 "`iss386_oi3_juart_landing_dependency` (★落点三选一★) · `iss386_oi2_b33_land_scope` (★`B33_PIN_LAND_1P27` 含不含 J_UART★) · "
                 "`iss386_oi11_seat_height_h` (★座体真实高 h = `[0数据]`★) · `iss386_oi12_cover_criterion_too_strict` (★⑤ 罩住判据对 THT 排针是否过严★) · "
                 "`iss386_oi13_y_zero_margin` (★Y 向零制造余量接受吗★) · `iss386_oi14_iss377_dp1_gap` (★`DP-1` 的 `3.4700` 要不要订正为 `4.0700`★) · "
                 "`iss386_oi15_pad1_displacement_attribution` (★`0.2441` 归属笔误★) ★ ⇒ "
                 "★**⇒ 这 8 条里有 5 条是【结构侧自己能答的技术题】(OI-2/OI-5/OI-12/OI-13/OI-14), "
                 "只有 OI-3(落点)/OI-11(座体高, 归 boss)/OI-15(笔误) 要 main/boss 拍 ⇒ "
                 "★**【结构侧能自答的那部分, 现在就该收口, 不要一起拖到老板回信** ★ ★\n\n"
                 "★**③ ISS-386 自己已经把最要紧的结论写死了 (★main 本机实读 `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md`★)★**: ★\n"
                 "★**「`J_DEBUG` 的『必须清空区 X 宽』三档算下来【红绿方向完全相同 (全红)】⇒ OI-5 选哪个只改【返工幅度】不改【方向】】** ⇒ "
                 "★**⇒ `J_DEBUG` 的结构件在那一趟【无论如何都要动】⇒ 【不存在「先只改 J_UART」的省事方案】** ★ ⇒ "
                 "★**⇒ 所以真正要交给结构侧的不是一个「选择题」, 而是【一份改件要求单】+【三档返工幅度的代价账】** ★\n\n"
                 "★**④ 结构侧那半还没答完的: 「那一趟」的结构件到底怎么改、怎么出件、改完哪几道闸会红★** ⇒ "
                 "★**main 本机实读: `MECH/` 与 `HW/PCB/` 下【没有任何一页】叫「改件要求单 / 出件要求单 / 结构件改动清单」** ⇒ "
                 "★`(grep -rln \"改件要求|出件要求单|改件清单|结构件改动清单\" MECH/*.md HW/PCB/*.md ⇒ 0 命中)` ★ ⇒ "
                 "★**⇒ 结构件那一侧现在有的是【判决】(红/绿), 缺的是【改件要求单 + 出件口径 + 闸】** ★ ★\n\n"
                 "★**⑤ 一处已有硬差额 (★main 实读, 你要复核★)★**: ★**`6.6100` 比官方 land 自己的 `F.CrtYd` `6.0900` 还大 `0.5200`** ⇒ "
                 "★**OI-12「⑤ 罩住判据对 THT 排针是否过严」不是空谈, 是有 `0.5200` 硬差额的技术题** ★\n\n"
                 + BOUND),
        "owner": "mech-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss379_q4_mech_opening_and_clearance", "iss386_oi2_b33_land_scope",
                      "iss386_oi12_cover_criterion_too_strict", "iss386_oi13_y_zero_margin",
                      "iss386_oi14_iss377_dp1_gap"],
        "task_brief": brief(BRIEF_389),
        "note": ("★2026-11-24 09:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ mech-lead 名下 ISS-386 已交卷 (mech.yaml 08:57 有本单登记) "
                 "⇒ 槽位待 main 签收后释放 ③ ★**trigger = `state/fragments/pm.yaml` 的 need "
                 "`iss379_q4_mech_opening_and_clearance` (★main 明令「两连接器合到一件答」+「答复窗口 = 板框上位问题的答复窗口」★) "
                 "+ ISS-386 交回的 8 条 OI (★其中 5 条结构侧能自答★)** ④ ★**main 本机实读 `MECH/` 与 `HW/PCB/` 下"
                 "「改件要求单/出件要求单/结构件改动清单」0 命中 ⇒ 结构件那侧现在只有判决没有要求单** ★\n"
                 + BOUND
                 + NOTE_TAIL),
    }

    for e in (e387, e388, e389):
        issues.append(e)

    # 原子写回 (★md5 守卫: 与开读时不一致 ⇒ 中止·不许覆盖 main 的并发写★)
    tmp = LOG + ".tmp_cronfb67_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)
    md5_now = md5(LOG)
    if md5_now != md5_before:
        os.unlink(tmp)
        print("★★中止 (rc=3): issue_log 在本脚本开读之后被改过 (md5 %s → %s) ⇒ 不写, 请重跑"
              % (md5_before, md5_now))
        return 3
    bak = LOG + ".bak_%s_cronfb67_open_387_388_389" % STAMP
    shutil.copy2(LOG, bak)
    os.replace(tmp, LOG)

    chk = yaml.safe_load(open(LOG, encoding="utf-8"))
    chk_issues = chk.get("issues") or []
    if len(chk_issues) != len(issues):
        print("★★中止 (rc=2): issue_log 写回条数不符 (期望 %d, 实际 %d)"
              % (len(issues), len(chk_issues)))
        return 2
    for eid in ("ISS-387", "ISS-388", "ISS-389"):
        hit = [i for i in chk_issues if i.get("id") == eid]
        if len(hit) != 1 or hit[0].get("status") != "fixing":
            print("★★中止 (rc=2): %s 写回后状态不对" % eid)
            return 2
    print("★ issue_log.yaml: 已落 3 单 (387/388/389 · status=fixing) · 条数 %d → %d · 备份 %s · 新 md5=%s"
          % (len(issues) - 3, len(chk_issues), os.path.basename(bak), md5(LOG)))

    # ---------------- dispatch_log (追加式·零 churn) ----------------
    dl_exists = os.path.exists(DLOG)
    dl_raw = yaml.safe_load(open(DLOG, encoding="utf-8")) if dl_exists else None
    if isinstance(dl_raw, list):
        dl_list = dl_raw
    elif isinstance(dl_raw, dict):
        dl_list = dl_raw.setdefault("dispatches", [])
    else:
        dl_list = []
    new_entries = []
    for e, ag in ((e387, "hw-lead"), (e388, "sw-lead"), (e389, "mech-lead")):
        new_entries.append({"issue": e["id"], "agent": ag, "at": time.strftime("%Y-%m-%d"),
                            "brief": e["task_brief"][:300]})
    if new_entries:
        chunk = yaml.safe_dump(new_entries, allow_unicode=True, sort_keys=False, width=200)
        with open(DLOG, "a", encoding="utf-8") as f:
            f.write(chunk)
    print("★ dispatch_log.yaml: 已追加 3 条派活记录")
    print(JOB)
    return 0


if __name__ == "__main__":
    sys.exit(main())
