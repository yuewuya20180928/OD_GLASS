#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1445_cronfb67af40_open_392_393_394.py
========================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-24 14:45
★**新开 3 条 + 直接落 fixing** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)
★**ISS-392 → sw-lead · ISS-393 → mech-lead · ISS-394 → hw-lead**

★**为什么现在要新开 (★main 本机实读·不抄任何 agent 报告★)**:
  ★① `python3 state/advance.py --json` ⇒ `internal: []` ⇒ 三个总工名下零 open 可派
  ★② ★**但这三个槽位不是真空, 是被【已交卷待签收】的 fixing 占着** ★
     (★ISS-388 sw-lead: 交卷页 `HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md` 27,809 B @ 12:56 在盘
       + 新闸 `SW/tools/check_sw_gate_health.py` 32,327 B @ 12:56 + 分片 sw.yaml 12 条 iss388 登记
       ⇒ ★**真交卷·待 main 签收**★ ⇒ 且 main 本机实跑该新闸 = 2/6 绿 (H1/H2/H3 红) ⇒ ★**它自己现在还是红的, 属交卷内容, 不属本单★)
     (★ISS-390 mech-lead: 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS390_FTS直插档座体外形与courtyard前提订正.md` 37,068 B @ 12:55 在盘
       + 新闸 `MECH/check_fts_seat_body_geometry.py` + 分片 mech.yaml ⇒ ★**真交卷·待 main 签收**★)
     (★ISS-391 hw-lead: 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md` 26,390 B @ 12:50 在盘
       + 新闸 `HW/check_fts_land_drill_same_batch.py` + 分片 hw.yaml ⇒ ★**真交卷·待 main 签收**★)
     ★**⇒ 这三个槽位一签收就空出来 ⇒ 本 job 趁窗口期把下一批活落到位 (★沿用 08:55/10:55/11:55 三轮同型先例★)★**
  ★③ ★**★上一轮同一个 job (14:01~14:11) 已经把两条 brief 写完并过了守卫 (ISS-392 / ISS-393), 但在【落台账 + 写第三条 brief + spawn】之前被掐断★**
     ⇒ ★**本脚本把那一轮没做完的活接上: 三条一起落 fixing, 然后 spawn ⇒ 一条都不丢★**
  ★④ ★**三条各自的开单依据 (★全是 main 本机实读撞出来的真病灶, 不是抄任何 agent 报告★)** ★
     ★**(甲) ISS-392 · sw-lead · SW 域门禁链覆盖率 ★**: 盘上 `SW/**/check_*.py` = ★**30**★ 道, 而 `state/gate_check.py` 链里只跑 ★**6**★ 道
       ⇒ ★**24 道 SW 闸从来没进过门禁链**★; 且链上 L222 跑的是 ★**v1**★ `check_sw_ref_reachability.py` (★ISS-332 查出 4 条洗白面的那一版★),
       收紧版 `check_sw_ref_reachability_v2.py` 根本没挂链 ⇒ ★**修好的那一版在盘上没人跑**★; 且 ISS-388 新建的元闸 `check_sw_gate_health.py`
       自己的 ROSTER 只扫了 ★**13**★ 道 ⇒ ★**它也看不见另外 17 道**★
     ★**(乙) ISS-393 · mech-lead · 「通用库件 courtyard 被当成厂件」扩散面 ★**: MECH 整条 3D 判决链吃的
       `4.8100`/`2.2700`/`F.CrtYd 6.0900`/`F.Fab 5.0800` 全是★**盘上通用 KiCad 库件**★的数 (★main 本机独立复核: 库件
       `PinHeader_1x0{4,2}_P1.27mm_Vertical.kicad_mod` ⇒ `(size 1 1)` + `(drill 0.65)` ⇒ 与 Samtec 无关★),
       而 `MECH/check_debug_seat_3d_fit.py` L848/L879 两处逐字写着「★而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900★」
       ⇒ ★**前提错误已从页扩散到闸源码**★ ⇒ 厂件外形 (ISS-390 已查到 `[官网]` 级) 一补上, 判决链每个数都要重算
     ★**(丙) ISS-394 · hw-lead · 座体选型结论【没传播】 ★**: main 早在 08:3x 已把 `FTSH-104-01-F-DV` / `FTSH-102-01-F-DV` 推翻
       (★官网单品页标题逐字「8 Pin, 2 Row, SMT」/「4 Pin, 2 Row, SMT」⇒ 双排贴片, 不是板侧要的单排直插★),
       ★**但那个「推翻」只写在 `state/issue_log.yaml` 的 `note_addendum` 里 ⇒ 板那一趟会读的 4 处活副本仍在说旧话★**:
       (甲) `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` L18/L62/L67/L73/L112 (★且该页「推翻/订正/§㊳」命中 = 0★)
       (乙) `state/fragments/hw.yaml` L5271-5272 (★那条【已闭】的 need 答案仍写「首选 FTSH-104-01-F-DV」★)
       (丙) `state/fragments/hw.yaml` L4346-4347 (★那条【未答】的 need 的三个选项【全是错的】⇒ 只能被答错★)
       (丁) `HW/check_debug_uart_seat_alignment.py` L397 (★一个【已签收闸】的 selftest 把被推翻的料号硬编码成【BOM 真源样本】★)
       ⇒ ★**⇒ BOM 型号栏此刻还是 `待定` ⇒ 现在纠正成本=改文档; 等落表后纠正 ⇒ 装错件 ⇒ 【板改两次】**★

★**并发写盘护栏**: `state/issue_log.yaml` 是 4.8 MB 大文件, main 的 webchat 会话可能同时在写
  ⇒ ★**本脚本在 `os.replace` 之前重算 md5, 与开读时不一致就中止 (rc=3)** ★

★**边界**: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板
          · 不改别人分片 · 只写 issue_log.yaml + dispatch_log.yaml + 本脚本自身
"""
import hashlib
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
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF_392 = "state/dispatch_briefs/ISS-392_sw_gate_chain_coverage.md"
BRIEF_393 = "state/dispatch_briefs/ISS-393_mech_fts_vs_generic_courtyard_delta.md"
BRIEF_394 = "state/dispatch_briefs/ISS-394_hw_seat_part_verdict_propagation.md"

JOB = ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 14:4x · "
       "★**新开 + 直接落 fixing (★铁律⑩-i 先落 fixing 再 spawn★) · "
       "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` 三条全 rc=0** ★ · "
       "★**纯分析 / 新建真相页 + 新建机器闸类 (零写板·零落表·零改既有闸·零改既有页正文·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★ · "
       "★**开单依据 = 三个槽位被【已交卷待签收】的 fixing 占着 (ISS-388/ISS-390/ISS-391) + 本 job 实读撞出的三条真病灶 ★** ★ "
       "★**接上一轮同一个 job (14:01~14:11) 被掐断的那两轮活: 两条 brief 已在盘, 本轮补第三条并三条一起落 + spawn** ★")


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

BOUND = ("★**本单性质**: 纯分析 + 新建真相页 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · "
         "零外发 · 不代拍 ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★\n"
         "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file <brief>` rc=0** ★\n")

BLOCK_REQ = ("★★**机检硬要求 (★main 本机实读 `state/gate_check.py` L47~L54★)**: 交卷页 B1~B6 六段必须齐全, "
              "且 `pick_handoff` 取【最新一份】评分 ⇒ ★★**最新一份自称 B 块结构但缺块 ⇒ 不许回退 ⇒ Q1 立刻掉** ★★ ⇒ ⇒ "
              "★**六段标题必须含 `REQUIRED_BLOCKS` 的关键词** (★`结论摘要`/`验收标准自评`/`证据分级`/`接口取值声明`/`未决项`/`自证复现命令`★) ★★\n")


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    for iid in ("ISS-392", "ISS-393", "ISS-394"):
        if iid in ids:
            print("★★%s 已存在 ⇒ 停下, 不重复开单" % iid)
            return 2
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    def brief(p):
        return open(os.path.join(PROJ, p), encoding="utf-8").read()

    # ---------------- ISS-392 · sw-lead ----------------
    e392 = {
        "id": "ISS-392",
        "title": ("★★[★新主线·PCB 线·SW 侧·纯分析+新建真相页+新建闸·零写板] SW 域【门禁链覆盖率 + 第三道病闸基线漂移】⇒ "
                  "把「板那一趟的 SW 侧护栏到底有几道真的在跑」变成机器可判 ★★"),
        "severity": "high",
        "source_blocker": "ISS-388",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·SW 侧·纯分析+新建真相页+新建机器闸·零写板·零落表·零改既有闸/既有页面正文]★\n\n"
                 "★**题 (来源 = ★**main 本机实跑 `state/gate_check.py` 门禁链, 逐条数出来的**★)★: ★\n\n"
                 "★**① 盘上 `SW/**/check_*.py` 共 ★**30**★ 道, 而门禁链里真正跑的只有 ★**6**★ 道 ⇒ ★★**24 道 SW 闸从来没进过门禁链**★★\n"
                 "★**② ★★更要命的一条: 链上 (L222) 跑的是 ★★`SW/tools/check_sw_ref_reachability.py` (★旧版★)★★, "
                 "而 ISS-332 (★已签收 verified★) 交出的 ★★收紧版 `SW/tools/check_sw_ref_reachability_v2.py` 根本没挂链★★ "
                 "⇒ ★★**闸链里跑的是【被查出 4 条洗白面】的那一版, 修好的那一版在盘上没人跑**★★\n"
                 "★**③ ★★再叠一层: ISS-388 刚交的那道【元闸】`SW/tools/check_sw_gate_health.py` 自己只扫了 ★**13**★ 道 SW 闸 "
                 "(★ROSTER 硬编码★) ⇒ ★★盘上另外 17 道 (★其中 15 道是带 `__main__` 的独立闸★) 它也看不见** ★★ "
                 "⇒ ★★**「元闸查闸坏了」这件事本身有 17 道的盲区**★★\n"
                 "★**④ ★★⇒ ★★**所以今天 SW 域的真相是: 板那一趟真会动板, 但绝大多数 SW 护栏那天根本不会跑; 跑着的那道里有已知洗白面; "
                 "连查闸有没有坏的那道元闸自己也只看了不到一半** ⇒ ★★**「板改完 SW 侧没人拦」这件事今天是【真】的, 不是假设**★★\n\n"
                 "★**⑤ 本单要交 4 件**: ★**(甲)** 新建真相页 `SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md` ★"
                 "★**(乙)** 新建机器闸 `SW/tools/check_sw_gate_chain_coverage.py` ★"
                 "★**(丙)** 交卷页 `HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md` (★B1~B6★) ★"
                 "★**(丁)** 分片 `state/fragments/sw.yaml` (★走 `state/frag_write.py`★)★ ★\n\n"
                 "★**⑥ ★★本单的地界 (★main 本机实读·本单【不许自己改】清单★)★★**: ★**本单零改既有闸的判据/阈值** "
                 "(★尤其 `state/gate_check.py` 的链本身、`check_sw_ref_reachability.py`、`check_sw_ref_reachability_v2.py`、"
                 "ISS-388 刚交的 `check_sw_gate_health.py`★) ⇒ ★**你要做的是【把覆盖率算清楚 + 建一个能查出「链里没挂的闸」的机器闸】, "
                 "不是【自己挂链】** ★\n\n"
                 "★**⑦ 已知会红的读数 (★main 本机实跑·不是你的闸故障★)**: ★**`python3 SW/tools/check_sw_ref_reachability_v2.py --selftest` "
                 "现在 rc=1 (反向用例 0/7 通过, 末行出现「有用例没抓到」) ⇒ 那是【基线漂移】, 本单不改它 ⇒ 交卷页要写明这是【已知基线红】不是本单引入** ★\n\n"
                 + BLOCK_REQ + BOUND),
        "owner": "sw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss388_third_sick_gate", "iss388_delta_selftest_convention"],
        "task_brief": brief(BRIEF_392),
        "note": ("★2026-11-24 14:4x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ sw-lead 名下 ISS-388 已交卷 (交卷页 27,809 B @ 12:56 + 新闸 32,327 B @ 12:56 "
                 "+ 分片 sw.yaml 12 条) ⇒ 槽位待 main 签收后释放 ⇒ 本 job 趁窗口期把下一批活落到位 "
                 "③ ★**本单 trigger = main 本机实跑门禁链逐条数出来的三条硬数字**: 盘上 SW 闸 30 道 vs 链里 6 道 / 链上跑 v1 而修好的 v2 没挂链 / "
                 "ISS-388 元闸自己的 ROSTER 只扫 13 道 ★\n"
                 "★**★本单的 brief 是上一个 job 同一轮 (14:01~14:11) 写完并过了命令存在性守卫的, 本轮接上落台账★** ★\n"
                 + BOUND + NOTE_TAIL),
    }

    # ---------------- ISS-393 · mech-lead ----------------
    e393 = {
        "id": "ISS-393",
        "title": ("★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建闸·零写板] 「通用库件 courtyard 被当成厂件」"
                  "这条前提错误的扩散面清账 + 判决链重算 ⇒ 把「换厂件之后哪些数要重算」变成机器可判 ★★"),
        "severity": "high",
        "source_blocker": "ISS-390",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表·零改既有闸/既有页面正文]★\n\n"
                 "★**题 (来源 = ★**main 本机实读撞出的一处「前提错误已扩散」**★)★: ★\n\n"
                 "★**① ISS-390 (★mech-lead · 今日 12:5x 已交卷★) 查到了厂件 (★Samtec `FTS` 单排直插★) 的真外形: "
                 "★**座体宽 X = N × 1.27 (★4 位 = `5.0800` · 2 位 = `2.5400`★) · 座体深 Y = `2.1600` · 绝缘体高 Z = `0.8600` · 柱高 `3.05`** ★ "
                 "`[官网]` (★官网机械/营销图 PDF·md5 `69d9415867cd642d6a6e07c6b755516b`★) ★\n"
                 "★**② ★★但 main 本机实读: MECH 整条 3D 判决链吃的 `4.8100` / `2.2700` / `6.0900` / `5.0800` / `2.6400` 全是"
                 "【盘上通用 KiCad 库件】的数, 与 Samtec 无关** ★\n"
                 "★**★main 本机独立复核 (★不是抄 ISS-390★)★**: ★**本机库件 "
                 "`/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` "
                 "⇒ `(drill 0.65)` + `F.CrtYd` 矩形 `(-1.55,-1.14)..(1.55,4.95)` ⇒ 宽 `3.10` 高 `6.09` ⇒ `6.0900`/`5.0800` 是第三方库件的数** ★★\n"
                 "★**③ ★★⇒ 而这条「前提错误」已经扩散到 §【已签收闸的源码字符串】里★ ⇒ ★★**main 本机实读 "
                 "`MECH/check_debug_seat_3d_fit.py`: 「官方」命中 ★**15**★ 处, 其中 L848/L879 两处逐字写着"
                 "「★而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200★」** ★★\n"
                 "★**④ ★★⇒ 后果: 「判据偏紧 `0.5200`」这个结论的【对照物是错的】 ⇒ 厂件外形一补上, 结构侧判决链上每一个拿这个对照物算出来的数都要重算** ★★\n"
                 "★**⑤ ★★且 ISS-390 自己算出一条本单之前没人算过的数**: ★**若「罩住」判据从罩铜箔扩到罩座体本体: "
                 "X 需 `6.8800`/`4.3400` (★各缺 `0.2700`★) · ★**Y 需 `3.9600` (★缺 `1.1600`★)** ★ · "
                 "而罩开口 Y `4.6000` 最多只容 `2.8000` ⇒ Y 向从「零余量卡死」变成「缺 `1.1600` 卡死」 ⇒ "
                 "★**`OI-13` 的「接受零余量」选项已不存在** ★★\n\n"
                 "★**⑥ 本单要交 4 件**: ★**(甲)** 新建真相页 `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` ★"
                 "★**(乙)** 新建机器闸 `MECH/check_fts_vs_generic_courtyard_delta.py` ★"
                 "★**(丙)** 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS393_通用库件与厂件对照物差集与判决链重算.md` (★B1~B6★) ★"
                 "★**(丁)** 分片 `state/fragments/mech.yaml` (★走 `state/frag_write.py`★)★ ★\n\n"
                 "★**⑦ ★★本单的地界 (★main 本机实读·本单【不许自己改】清单★)★★**: ★**本单零改既有闸** "
                 "(★尤其 `MECH/check_debug_seat_3d_fit.py` L848/L879 那两处逐字字符串★ — ★**那是 main 的地界**★) ⇒ "
                 "★**你要做的是【把差集算清楚 + 建一个能查出「判决链还在拿通用件当厂件」的机器闸】, 不是【自己改那两处字符串】** ★\n\n"
                 "★**⑧ ★★与 ISS-390 的关系 (★必须说清, 否则会被当成重复劳动★)★★**: ★**ISS-390 查的是【厂件真值】(官网一级)** ⇒ "
                 "★**本单查的是【判决链的对照物错在哪、哪些数要重算】(差集与扩散面)** ⇒ ★★**两单互补, 不许互相替代; 本单要独立复核 ISS-390 的数, 不许只抄** ★★\n\n"
                 + BLOCK_REQ + BOUND),
        "owner": "mech-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss386_oi12_cover_criterion_too_strict", "iss386_oi11_seat_height_window",
                      "oi387_4_fts_seat_body_outline"],
        "task_brief": brief(BRIEF_393),
        "note": ("★2026-11-24 14:4x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ mech-lead 名下 ISS-390 已交卷 (交卷页 37,068 B @ 12:55 + 新闸 + 分片 mech.yaml) "
                 "⇒ 槽位待 main 签收后释放 ⇒ 本 job 趁窗口期把下一批活落到位 ③ ★**本单 trigger = main 本机独立复核库件 `.kicad_mod` 撞出**: "
                 "MECH 判决链吃的 `6.0900`/`5.0800` 是【通用 KiCad 库件】的数 (★`(size 1 1)` + `(drill 0.65)`★) ⇒ "
                 "★**且该前提错误已扩散到已签收闸 `MECH/check_debug_seat_3d_fit.py` L848/L879 的源码字符串** ★\n"
                 "★**★本单的 brief 是上一个 job 同一轮 (14:01~14:11) 写完并过了命令存在性守卫的, 本轮接上落台账★** ★\n"
                 + BOUND + NOTE_TAIL),
    }

    # ---------------- ISS-394 · hw-lead ----------------
    e394 = {
        "id": "ISS-394",
        "title": ("★★[★新主线·PCB 线·HW 侧·纯分析+新建真相页+新建闸·零写板] 座体选型结论【只写在 issue_log 里, 没落到活页面/已闭答案/"
                  "未答 need/闸源码】⇒ 那条被推翻的结论现在是【活的】⇒ 把「结论被推翻后活副本必须被点名」变成机器可判 ★★"),
        "severity": "high",
        "source_blocker": "ISS-380",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·HW 侧·纯分析+新建真相页+新建机器闸·零写板·零落表·零改既有闸/既有页面正文]★\n\n"
                 "★**题 (来源 = ★**main 本机实读撞出的「结论没传播」**★)★: ★\n\n"
                 "★**① 板那一趟要填 BOM 型号栏 (`J_DEBUG` 行 71 / `J_UART` 行 77) ⇒ 型号栏此刻是 `待定` ⇒ "
                 "谁填、填什么, 决定了【板那一趟到底装哪颗件】★**\n"
                 "★**② ★★而 `state/fragments/hw.yaml` 里那条【还没答】的 need `iss380_board_trip_bom_part_fill` (★`to=main`★) 问的却是: "
                 "「★`J_DEBUG`/`J_UART` 按板侧真值档 (★`FTSH-104-01-F-DV` / `FTSH-102-01-F-DV`★) 还是 Cortex-10 2×5 档 "
                 "(`FTSH-105-01-L-DV-K`) ?」⇒ ★★**这个问题里【没有一个选项是对的】 ⇒ 它【只能被答错】★** ★★\n"
                 "★**③ ★★而 main 早在 2026-11-24 08:3x 就已经把那两个料号【推翻】了 (★main 本机实查厂商官网单品页标题 + Mouser/DigiKey 参数表★)**: "
                 "★**`FTSH-104-01-F-DV` 官网单品页标题逐字 = 「.050in/1.27mm Micro Header Strip, 8 Pin, 2 Row, SMT」+ "
                 "DigiKey「Number of Positions 8 / Number of Rows 2 / Surface Mount」⇒ 【8 脚双排贴片】, 不是板侧要的单排直插★** ★\n"
                 "★**④ ★★⇒ ★★**「推翻」这件事只写在 `state/issue_log.yaml` 的 `note_addendum` 里 ⇒ ★★**它没有落到任何一个"
                 "【板那一趟会读的文件】上** ⇒ ⇒ ★★**真相与活页面【不一致】⇒ 那一趟若照活页面填 BOM ⇒ 装上一颗 8 脚双排贴片 ⇒ "
                 "排针插不进 ⇒ 【板改两次】** ★★\n"
                 "★**⑤ ★★main 本机实读, 「活副本」不止一处, 至少 4 处 (★逐条给了行号★)**: ★★**(甲)** "
                 "`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` L18/L62/L67/L73/L112 —— ★**D-1/U-1 仍标「首选候选」, "
                 "且该页【零个「推翻/订正/§㊳」字样】⇒ 读不到任何推翻痕迹** · ★★**(乙)** `state/fragments/hw.yaml` L5271-5272 —— "
                 "★**那条【已闭】的 need `iss377_oi10_vendor_part_numbers` 的答案原文仍写「J_DEBUG 首选 Samtec `FTSH-104-01-F-DV`」"
                 "⇒ 【一个已被推翻的结论被标成「已闭」】** · ★★**(丙)** `state/fragments/hw.yaml` L4346-4347 —— "
                 "★**那条【未答】的 need 选项【全是错的】** · ★★**(丁)** `HW/check_debug_uart_seat_alignment.py` L397 —— "
                 "★**一个【已签收闸】的源码里, 把 `Samtec FTSH-104-01-F-DV` 硬编码成【BOM 真源样本】⇒ 那道闸的 selftest 现在【在教人填一颗被推翻的料号】**★★\n"
                 "★**⑥ ★★⇒ ★★**结论: 【推翻是「正确的」, 但它【没传播】⇒ 「板只改一次」那一趟的读数面【仍是错的】★ ⇒ "
                 "本单要做的不是再查一遍料号 (★ISS-380/383/387 已经查过三轮了★), 而是 ★**把「一条结论被推翻后, 它的活副本必须被点名」"
                 "这件事变成机器可判**★ ★\n\n"
                 "★**⑦ 本单要交 4 件**: ★**(甲)** 新建真相页 `HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md` (★§0~§6 + 机器块★) ★"
                 "★**(乙)** 新建机器闸 `HW/check_seat_part_verdict_propagation.py` (★K0~K6 + ≥10 条反向用例, 其中 ≥3 条专打 K1/K2/K3 漏项★) ★"
                 "★**(丙)** 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md` (★B1~B6★) ★"
                 "★**(丁)** 分片 `state/fragments/hw.yaml` (★走 `state/frag_write.py`★)★ ★\n\n"
                 "★**⑧ ★★本单的地界 (★main 本机实读·本单【不许自己改】清单★)★★**: ★**本单零改既有页面正文** (★尤其 "
                 "`..._DEBUG_UART_SEAT_PART_TRUTH.md` / `..._ALIGNMENT.md` / `..._FTS_SINGLE_ROW_LAND_TRUTH.md`★) ⇒ ★**你只【登记】那 4 处该怎么改, "
                 "【不许自己改】** · ★**零改既有闸** (★尤其 `HW/check_fts_single_row_land_truth.py` — ★**它 K4 的命门已经打对了**★ / "
                 "`HW/check_debug_uart_seat_truth.py` / `HW/check_debug_uart_seat_alignment.py`★) ⇒ ★**你要【新建】另一面的闸, 不许动它们** ★\n\n"
                 "★**⑨ 已知会红的读数 (★main 本机实跑·不是你的闸故障★)**: ★**闸的 K3 (★「未答 need 的选项里必须至少有一个满足板侧真值档的选项」★) "
                 "正向跑【必然红】⇒ 因为现状【就是这样】⇒ 交卷页要写明【K3 红是预期, 等 main 落完订正块才转绿】★ ★★**不许为了让它绿而放宽判据** ★\n\n"
                 + BLOCK_REQ + BOUND),
        "owner": "hw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss380_board_trip_bom_part_fill", "iss377_oi10_vendor_part_numbers",
                      "iss387_oi2_drill_change_same_batch"],
        "task_brief": brief(BRIEF_394),
        "note": ("★2026-11-24 14:4x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ hw-lead 名下 ISS-391 已交卷 (交卷页 26,390 B @ 12:50 + 新闸 + 分片 hw.yaml) "
                 "⇒ 槽位待 main 签收后释放 ⇒ 本 job 趁窗口期把下一批活落到位 ③ ★**本单 trigger = main 本机实读撞出的「结论没传播」**: "
                 "main 08:3x 已推翻 `FTSH-104-01-F-DV`/`FTSH-102-01-F-DV` (★官网单品页标题逐字「8 Pin, 2 Row, SMT」★), "
                 "★**但那个推翻只写在 `state/issue_log.yaml` 的 `note_addendum` 里 ⇒ 4 处活副本仍在说旧话 (真相页 L62/L67/L73/L112 + "
                 "hw.yaml L5271 已闭答案 + hw.yaml L4346 未答 need 的错选项 + `check_debug_uart_seat_alignment.py` L397 硬编码样本)★** "
                 "④ ★**⇒ BOM 型号栏此刻还是 `待定` ⇒ 现在纠正成本=改文档; 等落表后纠正 ⇒ 装错件 ⇒ 【板改两次】** ★\n"
                 "★**★本单的 brief 是本轮 (14:4x) 新写的, 命令存在性守卫 rc=0★** ★\n"
                 + BOUND + NOTE_TAIL),
    }

    # ---- 原子写回 (★md5 守卫: 与开读时不一致 ⇒ 中止·不许覆盖 main 的并发写★) ----
    if md5(LOG) != md5_before:
        print("★★ issue_log.yaml 在本脚本运行期间被改 (md5 变了) ⇒ 中止 (rc=3), 不写盘")
        return 3
    bak = LOG + ".bak_%s_cronfb67_open_392_393_394" % STAMP
    shutil.copy2(LOG, bak)
    out = []
    for e in (e392, e393, e394):
        out.append(dump_entry(e))
    src = open(LOG, encoding="utf-8").read()
    txt = src.rstrip("\n") + "\n" + "".join(out)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    print("✅ issue_log 追加成功: ISS-392 (sw-lead) + ISS-393 (mech-lead) + ISS-394 (hw-lead) · status=fixing (★零撞车窗口★)")
    print("   备份: %s" % os.path.basename(bak))

    # ---- dispatch_log 追加 (★幂等: 同 (issue, task_name) 不重复★) ----
    raw2 = open(DLOG, encoding="utf-8").read()
    if isinstance(raw2, list):
        entries, shape = raw2, "list"
    elif isinstance(raw2, dict):
        entries = raw2.setdefault("dispatches", [])
        shape = "dict"
    else:
        entries, shape = [], "list"

    new_entries = [
        {
            "issue": "ISS-392",
            "agent": "sw-lead",
            "at": "2026-11-24 14:45",
            "brief": ("★★[新开] SW 域【门禁链覆盖率 + 第三道病闸基线漂移】⇒ 把「板那一趟的 SW 侧护栏到底有几道真的在跑」变成机器可判 ★★"
                      "★★**纯分析 + 新建真相页 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸/既有页正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"),
            "brief_file": BRIEF_392,
            "job": JOB,
            "status_note": ("★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_iss392",
            "dispatched_at": "2026-11-24 14:45",
            "redispatch_zombie": False,
            "carried_over_from": ("★**本条 brief 是上一个 job 同一轮 (2026-11-24 14:01~14:11) 写完并过了命令存在性守卫 (rc=0) 的, "
                                  "但那个 job 在【落台账 + spawn】之前被掐断 ⇒ 本轮 (14:4x) 接上落台账 + spawn★**"),
        },
        {
            "issue": "ISS-393",
            "agent": "mech-lead",
            "at": "2026-11-24 14:45",
            "brief": ("★★[新开] MECH 侧【「通用库件 courtyard 被当成厂件」这条前提错误的扩散面清账 + 判决链重算】⇒ 把「换厂件之后哪些数要重算」变成机器可判 ★★"
                      "★★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸/既有页正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"),
            "brief_file": BRIEF_393,
            "job": JOB,
            "status_note": ("★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_iss393",
            "dispatched_at": "2026-11-24 14:45",
            "redispatch_zombie": False,
            "carried_over_from": ("★**本条 brief 是上一个 job 同一轮 (2026-11-24 14:01~14:11) 写完并过了命令存在性守卫 (rc=0) 的, "
                                  "但那个 job 在【落台账 + spawn】之前被掐断 ⇒ 本轮 (14:4x) 接上落台账 + spawn★**"),
        },
        {
            "issue": "ISS-394",
            "agent": "hw-lead",
            "at": "2026-11-24 14:45",
            "brief": ("★★[新开] HW 侧【座体选型结论只写在 issue_log 里, 没落到活页面/已闭答案/未答 need/闸源码】⇒ 那条被推翻的结论现在是【活的】★★"
                      "★★**纯分析 + 新建真相页 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸/既有页正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"),
            "brief_file": BRIEF_394,
            "job": JOB,
            "status_note": ("★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_iss394",
            "dispatched_at": "2026-11-24 14:45",
            "redispatch_zombie": False,
            "carried_over_from": ("★**本条 brief 是本轮 (14:4x) 新写的 (★上一轮被掐断在写第三条之前★), 命令存在性守卫 rc=0★**"),
        },
    ]
    added = 0
    for entry in new_entries:
        dup = any(isinstance(e, dict) and e.get("issue") == entry["issue"]
                   and e.get("task_name") == entry["task_name"] for e in entries)
        if dup:
            print("★已存在同 task_name 条目 ⇒ 不重复追加: %s" % entry["issue"])
            continue
        entries.append(entry)
        added += 1
    if added:
        bak2 = DLOG + ".bak_%s_cronfb67_open_392_393_394" % STAMP
        shutil.copy2(DLOG, bak2)
        fd, tmp2 = tempfile.mkstemp(dir=os.path.dirname(DLOG), prefix=".dispatch_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                if shape == "dict":
                    raw2["dispatches"] = entries
                    yaml.safe_dump(raw2, f, allow_unicode=True, sort_keys=False)
                else:
                    yaml.safe_dump(entries, f, allow_unicode=True, sort_keys=False)
            os.replace(tmp2, DLOG)
        finally:
            if os.path.exists(tmp2):
                os.unlink(tmp2)
        print("✅ dispatch_log 追加成功 (shape=%s) · 新增 %d 条" % (shape, added))
    else:
        print("★dispatch_log 零新增 ⇒ 未写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
