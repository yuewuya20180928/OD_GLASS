#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★_apply_20260725_0355_cronfb67af40_sign409_open412_413.py★

★**job**: cron `fb67af40` (ARS45 队列自动派活 · 每 30 分钟) · 2026-11-25 03:55
★**做什么**: ① 签收 ISS-409 (hw-lead · 本机独立复核, 不抄任何 agent 报告)
            ② 新开 ISS-412 (hw-lead) / ISS-413 (mech-lead) (纯查证+纯分析+新建真相页+新建机器闸 · 零写板 · 零落表)

★**铁律**:
  - ① 零写板 / 零落表 (只动 issue_log) / 零改既有闸 / 零改既有页正文 / 零挂链 / 零外发
  - ② CAS 守卫 (两层): ★写盘前【文件级 md5 对拍】(★防兄弟 job 并发写台账★) + 写回后【逐条条目 md5 对拍】
  - ③ 原子写: 先写 .tmp 再 os.replace
  - ④ 幂等: 已签收 / 已存在 ⇒ 跳过 (不重复写)
"""
import hashlib
import os
import shutil
import sys
import datetime as dt

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
TODAY = "2026-11-25"
DUE = "2026-11-26"
NOW = "2026-11-25 03:55"


def entry_md5(it):
    return hashlib.md5(yaml.safe_dump(it, allow_unicode=True, sort_keys=True).encode("utf-8")).hexdigest()


def file_md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# ============================================================ 签收 (main 本机独立复核读数)
SIGN = {
    "ISS-409": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 03:5x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `HW/check_onepass_release_chain_teeth.py` `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` "
            "(★main 实跑 tail 逐字: 「正向 1 条 + 反向 20 条 = 21 条 (失败 0 条) / ALL TESTS PASS」★)** ★ ⇒ "
            "★**交卷页在盘 (67,367 B · `HANDOFF/2026-11-25_hw-lead_ISS409_放行链牙齿清账与闸.md`) + "
            "真相页在盘 (64,482 B · `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md`) + "
            "新闸在盘 (58,081 B) + 自有分片 `state/fragments/hw.yaml` 命中 iss409 17 处** ★ ⇒ "
            "★**零挂链自证: `grep -c check_onepass_release_chain_teeth state/gate_check.py` = 0** ★ ⇒ "
            "★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (19 天) "
            "+ 网表/脚表/BOM 未变 + `state/outbox/` 最新文件仍是 11-11 (零外发) ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 未代老板拍板** ★ "
            "★ ⇒ `state/gate_check.py` rc=0 (Q1 18/18 · main 03:4x 实跑)** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 03:55 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·零挂链·零外发·未代老板拍板★)"
        ),
    },
}

SIGN_NOTE = (
    "★★2026-11-25 03:55 cron fb67af40 (ARS45 队列自动派活) · main 独立复核签收 (★追加式·老字一字未删★)★★\n"
    "★本机实跑读数 (★不抄任何 agent 报告★)★: 新闸 `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (正向 1 + 反向 20 = 21) · "
    "★交卷页 67,367 B + 真相页 64,482 B + 新闸 58,081 B 三件在盘 · 自有分片命中 17 · 零挂链 (grep=0) · "
    "★板 md5/mtime/size 三证与基线逐字相同 (19 天未动) · `state/outbox/` 未动 · `state/gate_check.py` rc=0 (Q1 18/18) ⇒ "
    "★零写板 · 零落表 · 零挂链 · 零外发 · 不代拍 · 不自签★\n"
    "★**签收只解「这条已交卷」, 不解「这道新闸已挂链」** ⇒ ★**挂链是 main 的地界, 另派** ★"
)

# ============================================================ 新开两条
NEW = [
    {
        "id": "ISS-412",
        "owner": "hw-lead",
        "severity": "high",
        "title": (
            "★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "「板那一趟」【板侧改动全集有没有漏项】: 下料前一票否决项 ⇒ 板侧项清单 的【双向差集】—— "
            "`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §附录 (ISS-354) 的 5 条否决项里, "
            "★**V-1-② (板侧 4 个 SoM 座没有 pin-1 极性丝印: [实测] 板上 `J_SOM_P1..P4` 只有 F.Fab 外框 22.6×3.2, 一条 F.SilkS 都没有; "
            "[官网] Hirose 「NOT polarized」⇒ 装反 = 101 处硬短)** ★ 与 "
            "★**V-3c (两只【必装】负载开关 `U_EN_SW`/`U_PWR_SW` 的 land 还是通用模板: 板面 0.6×0.9 双排 1.27 vs [官网] UQFN-4 RAA 0.85×0.75 @0.4 ⇒ 实物落不进去)** ★ "
            "★**既不在 §2 的 33 条板侧清单 (grep 丝印/silk = 0 命中; `U_PWR_SW` 全文只出现 2 次且都在 V-3c 段内), "
            "也不在作业包 §0.2 ③ 的 7 个板侧改动子项, 也不在 26 个 `MARKERS` 里 (只有 `U_EN_SW`), "
            "更不在来源单全集 `SOURCES` 里 (没有 ISS-354 ⇒ 想落成清单条目会被判「来源不明」直接判红)** ★ "
            "⇒ ★**没有任何一道机器闸看得见它们 ⇒ 板那一趟会漏做 ⇒ 板白打 + 板 md5 变第二次** ★★"
        ),
        "brief": "ISS-412_hw_veto_to_boardside_gap_audit.md",
        "need_keys": [
            "iss412_veto_to_boardside_bidirectional_diff_table",
            "iss412_marker_blind_spot_named_list",
            "iss412_preflight_source_set_patch_spec",
        ],
        "note": (
            "★**2026-11-25 03:55 cron fb67af40 (ARS45 队列自动派活) 新开** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0 (★台账 16 条 open 的 owner = boss 6 + main 10 ⇒ 全在可派域外 ⇒ 队列真空, 不是被占位挡住★); "
            "② 本脚本先签收 ISS-409 (hw-lead 已交卷) ⇒ 释放 hw-lead 槽位; mech-lead 槽位自 ISS-410 (兄弟 job 03:4x 已签收) 起空; "
            "③ ★**本单的题 = 【板侧改动全集 与 否决项 的差集】** (★ISS-404 查闸挂链 / ISS-406 查门禁链调用档位 / ISS-409 查放行链调用档位 ⇒ 三者查的都是【闸】, 本单查的是【板侧项清单 + 作业包 §0.2 ③ + 否决项清单】⇒ 不重复★)\n"
            "★**本机实测依据 (★全部可复现★)★: ① `PREFLIGHT.md` L1063 逐字「板侧 4 个座【没有 pin-1 丝印三角 / 缺口 / 极性标注】… 一条 F.SilkS 都没有」+ L1097 对策逐字「用板侧丝印 + 装配工序 + 上电前检查来挡」; "
            "② `PREFLIGHT.md` L1090 V-2 实测「两排一反 = 101 对相邻脚里 101 处一端 GND 一端带电 ⇒ 硬短」; "
            "③ `PREFLIGHT.md` L1120-L1124 V-3c 实测板面 land 0.6×0.9 双排 1.27 vs [官网] TI UQFN-4 RAA 0.85×0.75 @0.4 pitch; "
            "④ `grep -n \"丝印\\|silk\" HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ⇒ 只在 §附录命中, §2 逐条表 0 命中; "
            "⑤ `grep -c U_PWR_SW HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` = 2 且都在 V-3c 段内 ⇒ §2 里没有它; "
            "⑥ `HW/check_onepass_preflight_coverage.py` L86-L92 `MARKERS` 26 个里有 `U_EN_SW` 无 `U_PWR_SW`; L98-L100 `SOURCES` 11 个里无 `ISS-354` ⇒ L375-L378「来源不明」判红; "
            "⑦ `state/gen_pcb_netlist_board.py` L447 逐字「位号/值文字放 F.Fab 并隐藏 ⇒ 丝印层只留人工加的装配标识」⇒ 加极性标注是【会动板 md5】的板侧动作; "
            "⑧ 板 md5 `611b869e13518c3c023fb178f91a0075` / 4940213 / 2026-11-06 07:07:17.362193413 三证 19 天未动 ⇒ G1 仍开, 不许投板\n"
            "★**本单【不许做】**: 不许改 PREFLIGHT / WORKPACKET 正文 · 不许改 `HW/check_onepass_preflight_coverage.py` (含 `MARKERS`/`SOURCES`/`WP02_BINDING`) · 不许写板 · 不许挂链 · 不许外发 · 不许代拍 ⇒ 只出【规格 + 新闸 + 精确到行的补丁建议】交 main★\n"
            "★**本单属「板只改一次」纪律 ① (纯分析/作业包类, 不动板)★**"
        ),
    },
    {
        "id": "ISS-413",
        "owner": "mech-lead",
        "severity": "high",
        "title": (
            "★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "「板那一趟」【MECH 侧 4 个 `[0数据]` 前提格收口】: MECH 判决链 17 个前提量里 `PQ13`/`PQ14`/`PQ15` (座体外形宽X/宽Y/高Z 绝缘体) + "
            "`PQ16` (板厚) 四格【无真值读取点】⇒ D1 判据直接判红 + 依赖图里 7 条边 (E01/E02/E03/E04/E05/E13/E15) 只挂得到「三量收样」这一层、挂不到具体数字 "
            "⇒ ★**4 格一改没人知道哪些数/闸/结论作废; 而那 5 道消费闸 (check_debug_seat_3d_fit / check_debug_seat_rework_spec / "
            "check_fts_seat_body_geometry / check_fts_vs_generic_courtyard_delta / check_fts_seat_sample_plan) 里 4 道对它们是【盲的】 "
            "(铜箔宽写死 4.81/2.27 + `parse_footprint_copper()` 全仓零调用) ⇒ 填错也照样绿** ★ "
            "⇒ ★**按老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信, 全靠自己查资料」: 本地就有 Hirose 官网快照 (`state/_os_snapshots/` 3 件) ⇒ 自己查官网拿 [官网] 真值; 查不到必须写降级方案, 不许把「等收样/等原厂」挂着当阻塞项** ★★"
        ),
        "brief": "ISS-413_mech_premise_0data_closure.md",
        "need_keys": [
            "iss413_pq13_15_seat_envelope_official_value_or_degraded_plan",
            "iss413_pq16_board_thickness_tier_cost_table",
            "iss413_five_consumer_gates_recompute_checklist",
        ],
        "note": (
            "★**2026-11-25 03:55 cron fb67af40 (ARS45 队列自动派活) 新开** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0 (★队列真空: 台账 open 的 owner 全在可派域外★); "
            "② mech-lead 槽位自 ISS-410 (兄弟 job 03:4x 已签收) 起空; "
            "③ ★**本单的题 = 【把 4 个 `[0数据]` 格的【值】补出来 + 补不出来的【降级方案】+ 一道保证它们不再悄悄空着的闸】** (★ISS-407 交的是依赖图/作废传播, ISS-410 交的是选档决策表 ⇒ 本单做【值 + 降级 + 闸】⇒ 不重复★)\n"
            "★**本机实测依据 (★全部可复现★)★: ① `MECH/BOARD_ONEPASS_VERDICT_PREMISE_DEPENDENCY.md` L37-L43 逐字 `PQ13`/`PQ14`/`PQ15`/`PQ16` 四格 `[0数据]` + 「无真值读取点 (ISS-397 三量实测档收样中)」+ L43「D1 直接判红 ⇒ 这不是闸故障, 这就是现状」; "
            "② 同页 L125 逐字 D2「4 个只能挂到『三量收样』这一层 ⇒ 登记了但没人用得上」; "
            "③ 同页 L109-L125 依赖边表 ⇒ 受影响边 = E01/E02/E03/E04/E05 (有闸消费) + E13/E15 (无闸直接消费); "
            "④ `MECH/check_debug_seat_3d_fit.py` L683/L686 写死 4.81/2.27 · `MECH/check_debug_seat_rework_spec.py` L120/L122/L579 写死 (L119 注释承诺「现读」但无 `.kicad_mod`) · `parse_footprint_copper()` L187 全仓零调用 ⇒ 4 道闸对 4 格是盲的; "
            "⑤ `ls -l state/_os_snapshots/` ⇒ `hirose_DF40C-100DS-0.4V(51).pdf` 642,596 B + `hirose_DF40C-100DP-0.4V(51).pdf` + `hirose_pages/` 都在盘 ⇒ ★**官网资料本地就有 ⇒ 零外发可查 [官网]**; "
            "⑥ 板厚 `PQ16` 的硬要求在台账 `ISS-126` (owner=main·open): 检修口净空 4.50 mm ⇒ 现状 4.90 档过 / 1.22 mm 档 4.48 破 ⇒ 本单只出代价表, **不代拍档位**; "
            "⑦ 板 md5 三证 19 天未动 ⇒ G1 仍开, 不许投板\n"
            "★**本单【不许做】**: 不许改 VERDICT_PREMISE_DEPENDENCY / PREMISE_TIER_DECISION_TABLE 正文 · 不许改 6 道既有 MECH 闸判据 · 不许代拍板厚档/座体选型 · 不许收样 · 不许发任何信 · 不许写板 · 不许挂链 ⇒ 只出【规格 + 新闸 + 补丁建议】交 main★\n"
            "★**本单属「板只改一次」纪律 ① (纯分析/作业包类, 不动板)★**"
        ),
    },
]


def main():
    if not os.path.exists(LOG):
        print("FATAL: issue_log 不存在", file=sys.stderr)
        return 2

    raw_bytes = open(LOG, "rb").read()
    pre_file_md5 = hashlib.md5(raw_bytes).hexdigest()
    log = yaml.safe_load(raw_bytes.decode("utf-8"))
    is_list = isinstance(log, list)
    items = log if is_list else (log.get("issues") or [])

    before = {it.get("id"): entry_md5(it) for it in items if isinstance(it, dict)}

    # ---------- ① 签收 ----------
    signed = []
    for it in items:
        if not isinstance(it, dict):
            continue
        iid = it.get("id")
        if iid not in SIGN:
            continue
        if it.get("status") == "verified":
            print(f"  [skip] {iid} 已 verified")
            continue
        spec = SIGN[iid]
        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_date"] = "2026-11-25 03:55"
        it["verify_result"] = spec["verify_result"]
        it["fix_ref"] = spec["fix_ref"]
        na = it.get("note_addendum")
        if not isinstance(na, list):
            na = []
        na.append({"at": NOW, "by": "main", "text": SIGN_NOTE})
        it["note_addendum"] = na
        signed.append(iid)

    # ---------- ② 新开 ----------
    existing = {it.get("id") for it in items if isinstance(it, dict)}
    opened = []
    for spec in NEW:
        iid = spec["id"]
        if iid in existing:
            print(f"  [skip] {iid} 已存在")
            continue
        bp = os.path.join(BRIEFS, spec["brief"])
        if not os.path.exists(bp):
            print(f"FATAL: brief 不存在 {bp}", file=sys.stderr)
            return 2
        brief_text = open(bp, encoding="utf-8").read()
        it = {
            "id": iid,
            "title": spec["title"],
            "severity": spec["severity"],
            "source_blocker": None,
            "desc": brief_text,
            "owner": spec["owner"],
            "need_keys": spec["need_keys"],
            "task_brief": brief_text,
            "note": spec["note"],
            "source_agent": "main",
            "verify_by": "main",
            "reporter": "main",
            "raised": TODAY,
            "due": DUE,
            "status": "open",
            "external": False,
            "dispatched_at": None,
        }
        items.append(it)
        opened.append(iid)

    if not signed and not opened:
        print("  [noop] 无需改动")
        return 0

    # ---------- ③ 备份 + 文件级 CAS + 原子写 ----------
    if file_md5(LOG) != pre_file_md5:
        print("FATAL: 文件级 CAS 失败 · 台账在我读之后被别处改过 (兄弟 job 并发?) ⇒ 本次不写",
              file=sys.stderr)
        return 3

    bak = LOG + ".bak_20260725_0355_cronfb67af40_sign409_open412_413"
    shutil.copy2(LOG, bak)

    out = yaml.safe_dump(items if is_list else log, allow_unicode=True, sort_keys=False, width=100)
    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out)
    os.replace(tmp, LOG)

    # ---------- ④ CAS 守卫: 除签收 + 新增外, 其余逐条 md5 必须不变 ----------
    chk = yaml.safe_load(open(LOG, encoding="utf-8").read())
    citems = chk if isinstance(chk, list) else chk.get("issues", [])
    after = {it.get("id"): entry_md5(it) for it in citems if isinstance(it, dict)}
    touched = set(signed) | set(opened)
    bad = []
    for iid, h in before.items():
        if iid in touched:
            continue
        if after.get(iid) != h:
            bad.append(iid)
    if bad:
        print(f"FATAL: CAS 守卫失败 · 下列条目被意外改动: {bad[:10]}", file=sys.stderr)
        return 3
    for iid in opened:
        if iid not in after:
            print(f"FATAL: 新增条目 {iid} 写回后不在盘", file=sys.stderr)
            return 3
    for iid in signed:
        if after.get(iid) == before.get(iid):
            print(f"FATAL: 签收条目 {iid} 未变", file=sys.stderr)
            return 3

    print(f"  签收 {len(signed)} 条: {signed}")
    print(f"  新开 {len(opened)} 条: {opened}")
    print(f"  台账条目数 {len(items)} → {len(citems)}")
    print(f"  CAS 守卫: 其余 {len(before) - len(touched)} 条逐条 md5 未变 ✔")
    print(f"  备份: {os.path.basename(bak)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
