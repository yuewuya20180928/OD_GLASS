#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0830_cronfb67_open_384_385_386.py
==================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-24 08:3x
★**新开 3 条 + 直接落 fixing** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)

★**为什么现在要新开 (★本机实读·不抄任何 agent 报告★)**:
  ★① `python3 state/advance.py --json` ⇒ `internal: []` ⇒ 三个总工名下零 open 可派
  ★② 台账实读 ⇒ hw-lead / sw-lead / mech-lead 全部 `open 0` / `fixing 0`
     (★main 2026-11-24 08:03:52 已把 ISS-380/381/382/383 全部签成 verified ⇒ 三个槽位真真空★)
  ★③ ★**三条 need 至今没人答** (★本机逐 key 实读 fragments★):
     · `iss229_mech_hw_pcb_outline_old_charge_numbers` (to=hw-lead · since 2026-11-16 · due 2026-11-19 · ★逾期 5 天★)
     · `iss229_mech_sw_evt_pwr05_charge_current_criterion` (to=sw-lead · since 2026-11-16 · due 2026-11-19 · ★逾期 5 天★)
     · `iss379_q4_mech_opening_and_clearance` (to=mech-lead · since 2026-11-24 · main ISS-379 签收裁决 ④⑤ 明确「合到一件答」)
  ★④ ★**三条都【不碰板】** ⇒ 合「板只改一次」纪律 ① (先派不动板的)

★**并发写盘护栏**: `state/issue_log.yaml` 是 4.8 MB 大文件, main 的 webchat 会话可能同时刻写它
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

BRIEF_384 = "state/dispatch_briefs/ISS-384_hw_charge_current_live_value_caliber.md"
BRIEF_385 = "state/dispatch_briefs/ISS-385_sw_evt_charge_current_criterion.md"
BRIEF_386 = "state/dispatch_briefs/ISS-386_mech_debug_seat_3d_fit_combined.md"

JOB = ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 08:3x · "
       "★**新开 + 直接落 fixing (★铁律⑩-i 先落 fixing 再 spawn★) · "
       "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★ · "
       "★**纯分析 / 作业包类 (零写板·零落表·零改既有闸·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★ · "
       "★**开单依据 = main 08:03:52 已签收 ISS-380/381/382/383 ⇒ 三槽位真真空 + 三条 need 至今没人答** ★")


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


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    for iid in ("ISS-384", "ISS-385", "ISS-386"):
        if iid in ids:
            print("★★%s 已存在 ⇒ 停下, 不重复开单" % iid)
            return 2
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    def brief(p):
        return open(os.path.join(PROJ, p), encoding="utf-8").read()

    # ---------------- ISS-384 · hw-lead ----------------
    e384 = {
        "id": "ISS-384",
        "title": ("★★[★新主线·PCB 线·HW 侧·纯文档+新建闸·零写板] 「板只改一次」那一趟的【充电电流档位活值口径收口】: "
                  "把 0.822 旧系数从三份 HW 活文档清干净 + 补 R10 闸的判定面盲区 ★★"),
        "severity": "high",
        "source_blocker": "ISS-229",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·HW 侧·纯文档+新建机器闸·零写板·零落表]★\n\n"
                 "★**题 (来源 = `state/fragments/mech.yaml` 的 need `iss229_mech_hw_pcb_outline_old_charge_numbers` · "
                 "★since 2026-11-16 · ★due 2026-11-19 · ★**已逾期 5 天** · ★**至今没人答**★)★: ★**mech-lead 当时只报不改, "
                 "原文写明「只报不改, HW 地界由 hw-lead 自己改」** ★ ⇒ ★**它至今没被 HW 侧接走** ★\n\n"
                 "★**main 本机实读出的病灶 (不抄任何 agent 报告)★**: ★**① `HW/PCB_OUTLINE_60x15.md` 有三处带 0.822 旧口径的活值** "
                 "(★§3.4 表 L142~L147 的 ICHG/单pin/余量列 · L149「390Ω 档充电 ~29.20min」 · §4.2 O-4 行 L178「1A 回流抬高 14-32mV」★) "
                 "★**② `HW/J_CHG_SELECTION.md` 四处** (L32/L89/L91/L197) ★**③ `HW/POWER_BUDGET_V3.md` 三处** (L360 方向反了的公式 / L477 / L524) "
                 "★**④ 最要紧的是【闸的判定面有洞】: `HW/check_netlist_selfconsistency.py` 的 R10 判据 (L295~L302) 只扫一个文件 "
                 "`chgspec` = `HW/CHARGE_BOARD_SPEC.md` ⇒ 那本今天实测 `grep -c 0.822` = 0 (已清干净) ⇒ ★**R10 现在是绿的, 但它压根没看这三份文件**★** ★\n\n"
                 "★**分账纪律 (★本单核心★)★: ★**`HW/netlist_v1.csv` 里那 2 处 `0.822` 是【合法的历史说明】(「0.822 是它的倒数」) ⇒ 一个字都不许动** "
                 "★**(★动它 = 违「板只改一次」·★本单是文档口径单不是落表单★)** ★ · ★**`HW/PCB_OUTLINE_60x15.md` L151/L193 那两处是 ISS-230 留下的【作废标记】⇒ 只加不删** ★ "
                 "★**⇒ 本单只动「活值」格 ⇒ 新闸必须按【语境】判不许按【子串】判 (★否则会误伤那两处作废标记★)** ★\n\n"
                 "★**权威源 (只读·已签收)★: `MECH/HINGE_POWER_CALC.md` (ISS-229 verified) 的改正系数段 + `MECH/hinge_power_calc.json` 的 `rilim_table` "
                 "⇒ 方向修正 = `ICHG = η·(VBUS/VBAT)·IIN` = `1.216` @3.70V / `1.071` @4.20V (★旧的 `0.822` 是它的倒数·方向反了★) ★\n"
                 "★**★另有一条 main 本机实读出的硬事实 (★决定本单性质★)★: 网表 `HW/netlist_v1.csv` L47/L48 的 `R_ILIM` **2026-11-16 已落成 680Ω** (V-4 裁定) ⇒ "
                 "★**网表侧早就对了, 错的是这三份文档还在说 390Ω 档 + 0.822 系数 ⇒ 本单是【把文档追平到已落表的真值】, 不是【改一个数】** ★ ★"),
        "owner": "hw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss229_mech_hw_pcb_outline_old_charge_numbers"],
        "task_brief": brief(BRIEF_384),
        "note": ("★2026-11-24 08:3x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ hw-lead `open 0` / `fixing 0` (★main 08:03:52 已把 ISS-380/381/382/383 "
                 "全部签成 verified ⇒ 三个槽位真真空★) ③ ★**触发源 = `state/fragments/mech.yaml` 的 need "
                 "`iss229_mech_hw_pcb_outline_old_charge_numbers` (★since 2026-11-16 · due 2026-11-19 · ★**逾期 5 天** · "
                 "★**至今没人答**·★原文写明「只报不改, HW 地界由 hw-lead 自己改」★)★ ⇒ "
                 "★**main 本机实读三份 HW 活文档确认旧系数活值仍在 (PCB_OUTLINE_60x15.md / J_CHG_SELECTION.md / POWER_BUDGET_V3.md) + "
                 "R10 闸只扫 chgspec 一个文件 ⇒ 判定面有洞** ★\n"
                 "★**本单性质**: 纯文档口径订正 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍 "
                 "⇒ 合「板只改一次」纪律 ① (先派不动板的) ★\n"
                 "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file " + BRIEF_384 + "` rc=0** ★\n"
                 + NOTE_TAIL),
    }

    # ---------------- ISS-385 · sw-lead ----------------
    e385 = {
        "id": "ISS-385",
        "title": ("★★[★新主线·PCB 线·SW 侧·纯分析+新建闸·零写板] EVT `PWR-05` 充电电流判据与现行 `R_ILIM` 体系【不相容】的机器可判定化 ★★"),
        "severity": "high",
        "source_blocker": "ISS-229",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·SW 侧·纯分析+新建机器闸·零写板·零落表]★\n\n"
                 "★**题 (来源 = `state/fragments/mech.yaml` 的 need `iss229_mech_sw_evt_pwr05_charge_current_criterion` · "
                 "★since 2026-11-16 · ★due 2026-11-19 · ★**已逾期 5 天** · ★**至今没人答**★)★: ★**mech-lead 当时只报不改, "
                 "原文写明「只报不改, SW 地界由 sw-lead 自己改」** ★ ⇒ ★**它至今没被 SW 侧接走** ★\n\n"
                 "★**main 本机实读出的病灶 (不抄任何 agent 报告)★**: ★**① `SW/EVT_TEMPLATE.md` L131 的 `PWR-05` 写「充电电流 ≥ 1.5A @5V/2A 适配器」** ★ "
                 "★**② 但它与现行 `R_ILIM` 体系不相容: main 本机实读 `MECH/hinge_power_calc.json` 的 `rilim_table` 逐档算出 ⇒ "
                 "现行档 = 680Ω (V-4 裁定 2026-11-16, 已落表) ⇒ 电池侧 `ICHG` max = 0.697A ⇒ 1.5A 差 2.15×; 输入侧 `IINMAX` max = 0.574A ⇒ 差 2.61× "
                 "⇒ ★**无论它量的是哪个量, 这条判据在现值硬件上【永远判不过】** ★ ★\n"
                 "★**③ 而且这条不兼容【在旧 0.822 系数下就已存在】(390Ω max = 0.822A, 离 1.5A 更远) ⇒ ★**它【不是】ISS-229 造成的, 是一个【既存判据】** ★ ★\n"
                 "★**④ main 本机实读: `SW/EVT_TEMPLATE.md` 全文只有 L131 这一处提充电电流 ⇒ 单点判据, 不是散落各处的问题** ★\n"
                 "★**⑤ 一条不能忽略的前提 (main 本机实读网表 board 域)★: `U_CHG` (BQ25896) 与 `R_ILIM` 在网表里 board 域全是 `CHG_BOARD` "
                 "(★main 实读: `R_ILIM` 2 行 + `U_CHG` 8 行, **没有一行 board=MAIN_PCB**★) ⇒ "
                 "★**⇒ PWR-05 在 demo 主 PCB 那一趟到底【适不适用】是一个必须先答的前置问题** ★ ⇒ "
                 "★**★所以本单不许直接改判据数字; ★**必须先答「它量哪个量 / 适用不适用」, 再给三个改法候选 (甲降阈值 / 乙改判据对象 / 丙注明 demo 板不适用) ★ ★** ★\n\n"
                 "★**权威源 (只读·已签收)★: `MECH/HINGE_POWER_CALC.md` + `MECH/hinge_power_calc.json` 的 `rilim_table` (680Ω 档: IINMAX 0.5735 / "
                 "ICHG 0.6974 / 单 pin 0.3487 / 余量 1.43×) + `HW/netlist_v1.csv` L47/L48 (R_ILIM = 680Ω, V-4 裁定) ★"),
        "owner": "sw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss229_mech_sw_evt_pwr05_charge_current_criterion"],
        "task_brief": brief(BRIEF_385),
        "note": ("★2026-11-24 08:3x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ sw-lead `open 0` / `fixing 0` (★main 08:03:52 已把 ISS-380/381/382/383 "
                 "全部签成 verified ⇒ 三个槽位真真空★) ③ ★**触发源 = `state/fragments/mech.yaml` 的 need "
                 "`iss229_mech_sw_evt_pwr05_charge_current_criterion` (★since 2026-11-16 · due 2026-11-19 · ★**逾期 5 天** · "
                 "★**至今没人答**·★原文写明「只报不改, SW 地界由 sw-lead 自己改」★)★ ⇒ "
                 "★**main 本机实读 SW/EVT_TEMPLATE.md L131 的 PWR-05 判据 + 实读 `MECH/hinge_power_calc.json` 的 `rilim_table` 逐档算出 "
                 "「1.5A 在两个口径下都达不到」+ 实读网表 board 域 (U_CHG/R_ILIM 全在 CHG_BOARD)** ★\n"
                 "★**本单性质**: 纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · ★**零改 `SW/EVT_TEMPLATE.md` 正文 "
                 "(★判据要不要改是 main 地界·★本单只交页+闸·★提前单独改 = 中间态 = 制造 churn·★同款先例 ISS-379 Q9 / ISS-381 correction block 都是「与那一趟同批落」★)** ★ · "
                 "零外发 · 不代拍 ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★\n"
                 "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file " + BRIEF_385 + "` rc=0** ★\n"
                 + NOTE_TAIL),
    }

    # ---------------- ISS-386 · mech-lead ----------------
    e386 = {
        "id": "ISS-386",
        "title": ("★★[★新主线·PCB 线·MECH 侧·纯分析+新建闸+沙盒·零写板] 「板只改一次」那一趟的 `J_DEBUG` + `J_UART` 两连接器"
                  "【座体 / 开口 / 清空区 三件合到一件答】 ★★"),
        "severity": "high",
        "source_blocker": "ISS-379",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·MECH 侧·纯分析+新建机器闸+沙盒预演·零写板·零落表·零改已签收件]★\n\n"
                 "★**题 (来源 = `state/fragments/pm.yaml` 的 need `iss379_q4_mech_opening_and_clearance` · since 2026-11-24)★: ★**main "
                 "2026-11-24 06:0x 转给 mech-lead 的两问, 原文写明「两问都要 mech-lead 答, 且必须在「板那一趟」开工前答完」** ★ ⇒ "
                 "★**它至今没被接走** ★\n\n"
                 "★**两问 (main 本机实读 need 原文转述·不代裁)★**: ★**① `J_UART` 落点横移会不会挤掉 UART 罩开口 / 座体必须清空区? "
                 "② 官方 THT land 铜箔 X 宽 `2.2700` vs 座体必须清空区宽 `2.5400` ⇒ 每边余量 `0.1350` < `CRIT` `0.60` ⇒ 结构红灯 ⇒ "
                 "「板那一趟」的结构件怎么办** ★\n\n"
                 "★**main 本机实读到的三条 must (★本单真正的难点★)★**: ★\n"
                 "★**A · `J_DEBUG` 的「必须清空区 X 宽」在仓里有【三个数】 (`1.7750` 现状铜箔宽 / `4.0850` 现页四处 / `4.8100` 官方 THT 真 land) "
                 "⇒ 没有单一真源 ⇒ ★**结构件按哪个出件, 决定它会不会当场干涉 (每边超 `1.5175` vs `0.3625`, ★**差 4.18 倍**★)** ⇒ "
                 "★**★main 在 ISS-377 已登记 `OI-5` 问「以哪一个为准」· 至今未答 ⇒ 你【不许替 main 答】, 但你【必须把三个数各算一遍】把后果摊成表** ★ ★\n"
                 "★**B · 两件换 THT 后是【一红一绿】而判据方向【相反】 (`J_DEBUG` 走开口余量 `2.6950` 过阈 / `J_UART` 走罩住余量 `0.1350` 不过阈) "
                 "⇒ ★**★main 在 ISS-379 签收裁决里明确要求「把两连接器的座体/开口/清空区【合到一件】答 · 别分两票 · 同批改的板两个答案不能互相矛盾」** ★ "
                 "⇒ ★★★**⇒ 你【必须】把两件放在【同一张同源表】里一起答** ★★★ ★\n"
                 "★**C · `J_UART` 的落点是【互斥三选一】且 main 已挂起 (★ISS-379 签收裁决 ②「落点本单不定·前提没落」★) ⇒ "
                 "★**你的结论必须对三个候选【全部】成立, 不许只算一个** ⇒ ★**这是「与板那一趟同批」的必要条件 (板框上位问题落甲, 三个坐标才全有效)** ★ ★\n\n"
                 "★**板侧那半已交付 (⇒ 你不用重算板侧铜)★**: ★**三个候选落点 (ISS-379 §2.3 verified): rot 270 pad1 `(18.6000, 68.6000)` 余量 `0.2750` · "
                 "rot 90 pad1 `(18.4000, 68.4000)` 余量 `0.1155` · rot 90 pad1 `(18.3000, 68.6000)` 余量 `0.0447`** ★\n"
                 "★**两连接器现有真相数 (只读·已签收)★**: ★**`J_DEBUG` 开口 X `137.850..148.050` × Y `54.300..58.900`, 必须清空区 X `142.063..143.838` "
                 "× Y `55.330..57.870`, 官方 THT 铜箔 `4.8100` ⇒ 换 THT 后每边超 `1.5175`** ★ · ★**`J_UART` 开口 X `13.790..23.990` × Y `66.300..70.900`, "
                 "必须清空区 X `17.620..20.160` × Y `67.330..69.870`, 官方 THT 铜箔 `2.2700` ⇒ 换 THT 后罩住余量 `0.1350`** ★ "
                 "(★`CRIT`/`TOL` 真身在 `MECH/service_port_check.py` L126-L127, ★**不许写死**★) ★"),
        "owner": "mech-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss379_q4_mech_opening_and_clearance"],
        "task_brief": brief(BRIEF_386),
        "note": ("★2026-11-24 08:3x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ mech-lead `open 0` / `fixing 0` (★main 08:03:52 已把 ISS-380/381/382/383 "
                 "全部签成 verified ⇒ 三个槽位真真空★) ③ ★**触发源 = `state/fragments/pm.yaml` 的 need "
                 "`iss379_q4_mech_opening_and_clearance` (★since 2026-11-24 · ★**至今没人答**·★原文写明「两问都要 mech-lead 答, "
                 "且必须在「板那一趟」开工前答完」·★main ISS-379 签收裁决 ④⑤ 明确要求「合到一件答·别分两票」★)★ ⇒ "
                 "★**main 本机实读板侧三个候选落点 + 两连接器开口/清空区/官方 THT 铜箔宽 + ISS-377 同源判据链 + CRIT/TOL 真身** ★\n"
                 "★**本单性质**: 纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · ★**零改已签收件 (★ISS-371/374/376/377/382/295 六份已签收页只读★)** ★ · "
                 "零外发 · 不代拍 (★`OI-5` 与 `J_UART` 落点三选一【都不许你代拍】★) ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★\n"
                 "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file " + BRIEF_386 + "` rc=0** ★\n"
                 + NOTE_TAIL),
    }

    # ---------------- 落 issue_log (追加式·老字一字未删) ----------------
    raw2 = raw.rstrip("\n") + "\n" + dump_entry(e384) + dump_entry(e385) + dump_entry(e386)

    bak = LOG + ".bak_%s_cronfb67_open384_385_386" % STAMP
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
    for iid in ("ISS-384", "ISS-385", "ISS-386"):
        assert got.get(iid) == "fixing", (iid, got.get(iid))
    assert len(doc2.get("issues") or []) == len(issues) + 3, "条数不符"
    for i in issues:
        assert got.get(i.get("id")) == i.get("status"), ("status 被改", i.get("id"))
    print("★ issue_log 已落: 新开 ISS-384(hw-lead) / ISS-385(sw-lead) / ISS-386(mech-lead) 三条 = fixing "
          "(条数 %d → %d · 备份 %s · 新 md5=%s)"
          % (len(issues), len(doc2.get("issues") or []), os.path.basename(bak), md5(LOG)))

    # ---------------- 落 dispatch_log (追加式) ----------------
    ddoc = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert isinstance(ddoc, list), "dispatch_log 形状不是 list ⇒ 中止"
    bak2 = DLOG + ".bak_%s_cronfb67_open384_385_386" % STAMP
    shutil.copy2(DLOG, bak2)
    for iid, agent, briefp, desc in (
        ("ISS-384", "hw-lead", BRIEF_384,
         "★★[新开] 「板只改一次」那一趟的【充电电流档位活值口径收口】: 0.822 旧系数从三份 HW 活文档清干净 + 补 R10 闸的判定面盲区"),
        ("ISS-385", "sw-lead", BRIEF_385,
         "★★[新开] EVT PWR-05 充电电流判据与现行 R_ILIM 体系【不相容】的机器可判定化"),
        ("ISS-386", "mech-lead", BRIEF_386,
         "★★[新开] 「板只改一次」那一趟的 J_DEBUG + J_UART 两连接器【座体/开口/清空区 三件合到一件答】"),
    ):
        ddoc.append({
            "issue": iid, "agent": agent, "at": "2026-11-24",
            "brief": desc, "brief_file": briefp,
            "job": JOB,
            "status_note": ("★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则会挡住任何 job "
                            "给该 agent 再派活 ⇒ 零撞车窗口★"),
            "dispatched_at": "2026-11-24 08:3x",
            "redispatch_zombie": "False",
        })
    tmp2 = DLOG + ".tmp_%d" % os.getpid()
    with open(tmp2, "w", encoding="utf-8") as f:
        yaml.safe_dump(ddoc, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100000)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp2, DLOG)
    chk = yaml.safe_load(open(DLOG, encoding="utf-8").read())
    assert len(chk) == len(ddoc), "dispatch_log 条数不符"
    print("★ dispatch_log 已追加 3 条 (总条数 %d · 备份 %s)" % (len(chk), os.path.basename(bak2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
