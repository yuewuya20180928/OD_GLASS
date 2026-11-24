#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★_apply_20260725_0245_cronfb67af40_sign406_407_408_open409_410_411.py★

★**job**: cron `fb67af40` (ARS45 队列自动派活 · 每 30 分钟) · 2026-11-25 02:45~02:5x
★**做什么**: ① 签收 ISS-406/407/408 (main 本机独立复核, 不抄任何 agent 报告)
            ② 新开 ISS-409/410/411 (三域各一条 · 纯查证+纯分析+新建真相页+新建机器闸 · 零写板 · 零落表)

★**铁律**:
  - ① 零写板 / 零落表 (只动 issue_log + 自己的分片不动) / 零改既有闸 / 零改既有页正文 / 零挂链 / 零外发
  - ② CAS 守卫: 除 3 条签收 + 3 条新增外, 其余全部条目逐条 yaml 序列化 md5 必须逐字不变
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
DUE = "2026-11-27"

NOW = "2026-11-25 02:5x"

# ============================================================ 签收 (main 独立复核读数)
SIGN = {
    "ISS-406": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 02:4x~02:5x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `HW/check_onepass_gate_teeth.py` `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` "
            "(★反向用例 16/16 通过 = 正向 1 条 + 反向 15 条★)** ★ ⇒ "
            "★**「门禁链 18 道闸的实际调用档位 ⇒ 判据强度」这一轴, 今天第一次有了逐道台账 + fail-closed 闸** ★ ⇒ "
            "★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (19 天) "
            "+ 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 未变 ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**交卷页在盘 (37,976 B · `HANDOFF/2026-11-25_hw-lead_ISS406_验收链牙齿清账与闸.md`) + 新闸在盘 (46,141 B) "
            "+ 真相页在盘 + 自有分片 hw.yaml 命中 16** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 02:5x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·零挂链·零外发·未代老板拍板★)"
        ),
    },
    "ISS-407": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 02:4x~02:5x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `MECH/check_verdict_premise_dependency.py` `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` "
            "(★正向 2 条 + 反向 12 条★)** ★ ⇒ "
            "★**MECH 判决链的「前提 → 哪些数/闸/结论同时作废 + 谁负责重算」第一次成了机器可判的表** ★ ⇒ "
            "★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (19 天) "
            "+ 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 未变 ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**交卷页在盘 (38,497 B · `HANDOFF/2026-11-25_mech-lead_ISS407_判决链前提依赖与作废传播.md`) + 新闸在盘 (30,587 B) "
            "+ 真相页在盘 + 自有分片 mech.yaml 命中 16** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 02:5x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·零挂链·零外发·未代老板拍板★)"
        ),
    },
    "ISS-408": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 02:4x~02:5x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**`SW/tools/check_sw_board_md5_rebase_readiness.py` `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` "
            "(★反向用例 10/10 通过★)** ★ ⇒ "
            "★**「板 md5 重锚定守门闸自己病着」(H1 漏登记 4 处 + H4 漏登记 1 闸) 今天被修到 7/7 全绿** ★ ⇒ "
            "★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (19 天) "
            "+ 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 未变 ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**交卷页在盘 (36,061 B · `HANDOFF/2026-11-25_sw-lead_ISS408_板md5重锚定守门闸修可信.md`) "
            "+ 真相页 + 追加式收口 + 自有分片 sw.yaml 命中 14** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 02:5x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·零挂链·零外发·未代老板拍板★)"
        ),
    },
}

SIGN_NOTE = (
    "★★2026-11-25 02:5x cron fb67af40 (ARS45 队列自动派活) · main 独立复核签收 (★追加式·老字一字未删★)★★\n"
    "★本机实跑读数 (★不抄任何 agent 报告★)★: 三道新闸 `--selftest` 全部 rc=0 · 末行逐字 `ALL TESTS PASS` · "
    "★三份交卷页在盘 + 自有分片登记命中 (hw 16 / mech 16 / sw 14) · "
    "★板 md5/mtime/size 三证与基线逐字相同 (19 天未动) ⇒ 零写板 · 零落表 · 零挂链 · 零外发 · 不代拍 · 不自签★\n"
    "★**签收只解「这三条已交卷」, 不解「这三道新闸已挂链」** ⇒ ★**挂链是 main 的地界, 另派 (ISS-409/410/411 在跑)★"
)

# ============================================================ 新开三条
NEW = [
    {
        "id": "ISS-409",
        "owner": "hw-lead",
        "severity": "high",
        "title": (
            "★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "「板那一趟」【投产/放行链有没有牙齿】: `state/check_pcb_drc.py` 全仓调用档位清账 — "
            "投产链准入闸 `state/chain_gate.py` L296 逐字 `run([sys.executable, \"state/check_pcb_drc.py\"])` ⇒ 没有 `--strict` "
            "⇒ unconnected=45 恒判绿 ⇒ 「板那一趟」做完板侧同步后 ③PCB 环判绿 ⇒ 没布完的板也能下单 ⇒ 板改第二次 "
            "⇒ ★**全仓实测只有 `state/verify_and_release.sh` 一处带 `--strict`** ★★"
        ),
        "brief": "ISS-409_hw_release_chain_teeth_audit.md",
        "need_keys": [
            "iss409_release_chain_call_sites_ledger",
            "iss409_lenient_mode_false_green_verdict",
            "iss409_unrouted_blocks_release_patch_spec",
        ],
        "note": (
            "★**2026-11-25 02:5x cron fb67af40 (ARS45 队列自动派活) 新开** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0; "
            "② 三个槽位 (ISS-406/407/408) 的 agent 会话全部收工 (交卷页在盘 + transcript 静默) ⇒ ★**本脚本先签收这三条, 槽位全部释放**★; "
            "③ ★**本单的题 = 投产/放行链的调用档位** (★ISS-406 查的是【门禁链 18 道闸】, 本单查的是【投产/放行/巡检/候选验证/生成器写盘守卫】这条链 ⇒ 不重复★)\n"
            "★**本机实测依据 (★全部可复现★)★**: "
            "① `state/check_pcb_drc.py` L134-L139 逐字 `ok4 = (n_unc == 0) if strict else True` ⇒ 不带 `--strict` 恒真; "
            "② `state/chain_gate.py` L296 逐字无 `--strict`; "
            "③ `state/chain_gate.py` L301-L310 源码注释逐字「布线是否完成 (不阻塞\"准出\", 但要报出来)」⇒ `lay_txt` 不参与判定; "
            "④ `check_pcb_nets` 今天 rc=1 ⇒ ③PCB 今天红的是 C1 不是 DRC ⇒ **「未布线」这一项今天完全没参与判定**; "
            "⑤ 全仓扫 `check_pcb_drc.py` 调用点 ⇒ 只有 `state/verify_and_release.sh` 带 `--strict`; "
            "⑥ `state/finish_line.sh` L102 / `state/auto_release_if_ready.sh` L151 只 grep 日志文本、不自己跑 ⇒ 假绿会被二次放大成「放行依据」; "
            "⑦ 宽松档实测打「✅ C4 unconnected items = 45」+「✅ 全过 —— 图纸可下单」且 rc=0; "
            "⑧ 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime 2026-11-06 07:07:17.362193413 / size 4940213 (19 天未动); "
            "⑨ `state/stage_gate.py` 当前 G1 · 还差 1 项 = unconnected 45→0\n"
            "★**纪律 ① (先派纯分析/作业包类, 不动板)**: 本单零写板 · 零落表 · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签\n"
            "★**本单属 PCB 线·纯分析类** ★"
        ),
    },
    {
        "id": "ISS-410",
        "owner": "mech-lead",
        "severity": "high",
        "title": (
            "★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "「板那一趟」【前提量选档 ⇒ 下游作废传播】: 排针焊盘四档 (1.000/1.010/1.110/1.218) 至今未拍板, "
            "而 MECH 判决链七个数 + 两页现状值型判据 + 结构件出件依据已按 1.000 签收 ⇒ "
            "ISS-403 已逐字写死「pad ≥ 1.010 下【不成立】」而 7 道闸里 5 道对它完全盲 ⇒ "
            "四来源 (BOM/作业包/真相页机器块/板面 footprint) 今天连「这一格记没记」都对不上 ⇒ 板改第二次的结构性风险零闸可见 ★★"
        ),
        "brief": "ISS-410_mech_premise_tier_decision_table.md",
        "need_keys": [
            "iss410_premise_tier_four_sources_ledger",
            "iss410_tier_switch_recompute_checklist",
            "iss410_fab_capability_self_research_result",
        ],
        "note": (
            "★**2026-11-25 02:5x cron fb67af40 (ARS45 队列自动派活) 新开** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0; "
            "② 三个槽位 (ISS-406/407/408) 的 agent 会话全部收工 ⇒ ★**本脚本先签收这三条, 槽位全部释放**★; "
            "③ ★**本单的题 = 前提量的【当前档位】+【四来源一致性】+【换档的重算清单】** (★ISS-403 出的是矩阵不是闸; ISS-407 出的是依赖图但没接「选哪一档」这个入口 ⇒ 不重复★)\n"
            "★**本机实测依据 (★全部可复现★)★**: "
            "① `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` L59-L61 四档逐字 (1.000/1.010/1.110/1.218); "
            "② `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` L54-L56 逐字 = 现状真相页把 `1.000` 写进了现状值型判据; "
            "③ 同页 L119 逐字「在 `pad ≥ 1.010` 之下【不成立】⇒ 那两页的现状值型判据【已经陈旧】」; "
            "④ 同页 L29 逐字「2 层 1 oz 下限 `0.18` ⇒ `1.010` 不满足 ⇒ 需 `pad ≥ 1.070`」+「板厂是谁这一格至今 `[0数据]`」; "
            "⑤ 同页 L135 表 = 7 道闸里 5 道 A/B 两臂红项集合差集为空 ⇒ 对 pad 完全盲; "
            "⑥ 同页 L92-L99 七个数的逐档现值 + 推算式 (`3.8100 + pad` / `(2.5400 − pad)/2`); "
            "⑦ `HW/BOM_v1.csv:71/77` 逐字 = J_DEBUG/J_UART 的型号栏「待定」⇒ BOM 这一行压根没有 pad 尺寸这一格; "
            "⑧ `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L243 逐字 = 调试口开口/清空区/净距的数是按现状算的, 但那一段没写死 pad 档; "
            "⑨ `python3 MECH/check_mech_gate_hook_coverage.py` rc=1 (M2 红) ⇒ 29 道闸只挂 4 道; "
            "⑩ 板/网表/脚表/BOM 四指纹未动\n"
            "★**纪律 ① (先派纯分析/作业包类, 不动板)**: 本单零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签\n"
            "★**选哪一档是 main/老板的地界 ⇒ 本单只做决策表, 不选档 (机器块 decision_taken_here = not_decided_here)★**\n"
            "★**本单属 PCB 线·纯分析类** ★"
        ),
    },
    {
        "id": "ISS-411",
        "owner": "sw-lead",
        "severity": "high",
        "title": (
            "★★[★新主线·PCB 线·SW 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "「板那一趟」【必改面会打掉哪些闸】: 位号改名面 + 布线面 vs SW 域 31 道闸 — "
            "main 本机实测 8 道硬编位号字面量 (★`check_sw_ref_reachability_v2.py` 一道 58 处 + v1 55 处, 而链上跑的正是 v1·ISS-392 实测「v1_in_chain_v2_not_hooked」★) "
            "+ 10 道一个真源都不读 (只读真相页/账本) + 17 道读板面 (布线一落地基线就漂) ⇒ "
            "那一趟落地后 SW 侧静默失守, 今天零机器闸看得见 ★★"
        ),
        "brief": "ISS-411_sw_mustchange_face_impact.md",
        "need_keys": [
            "iss411_sw_gate_hardcoded_refdes_ledger",
            "iss411_mustchange_face_impact_matrix",
            "iss411_pre_trip_anchor_order_list",
        ],
        "note": (
            "★**2026-11-25 02:5x cron fb67af40 (ARS45 队列自动派活) 新开** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0; "
            "② 三个槽位 (ISS-406/407/408) 的 agent 会话全部收工 ⇒ ★**本脚本先签收这三条, 槽位全部释放**★; "
            "③ ★**本单的题 = 必改面 → 闸的判据失效** (★ISS-392 判覆盖率/ISS-388 判环境无关性/ISS-398 判 selftest 夹具 ⇒ 都不是这一轴★)\n"
            "★**本机实测依据 (main 自己扫源码, 零抄报告)★**: "
            "① `SW/tools/check_*.py` + `SW/check_*.py` 逐文件数 = 31 道; "
            "② 8 道硬编位号字面量 (逐处计数: v2 = 58 · v1 = 55 · sync = 20 · v2_selftest = 8 · shutdown = 6 · debug_pin_order = 2 · evt_charge = 1 · load_switch = 1); "
            "③ `python3 SW/tools/check_sw_gate_chain_coverage.py` rc=0 (7/7) ⇒ 输出逐字「链上位号可达性闸: v1_in_chain_v2_not_hooked」⇒ 链上跑的 v1 硬编 55 处; "
            "④ 10 道闸只读真相页/账本、零真源输入 (brightness_biosafety · r6_hardprot_selftest · iss250_rknn_target · iss355_convert_route · onepass_sw_release · rk3572_target_caliber · rknn_target_compat · sw09_patch_dryrun · sw_zero_copper_grade_consistency · timing_review_adc_sync); "
            "⑤ 输入面分布: 真相页 28 / 脚表网表 19 / 板面 17 / 台账 13 / BOM 11 / 固件源码 1; "
            "⑥ 板/网表/脚表/BOM 四指纹未动\n"
            "★**纪律 ① (先派纯分析/作业包类, 不动板)**: 本单零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签\n"
            "★**「哪几道闸要改 / 怎么改 / 挂不挂链」都是 main 的地界 ⇒ 本单只出影响面 + 排序清单★**\n"
            "★**本单属 PCB 线·纯分析类** ★"
        ),
    },
]


def entry_md5(it):
    return hashlib.md5(
        yaml.safe_dump(it, allow_unicode=True, sort_keys=True, width=100).encode("utf-8")
    ).hexdigest()


def main():
    if not os.path.exists(LOG):
        print("FATAL: issue_log.yaml 不在", file=sys.stderr)
        return 2

    raw = open(LOG, encoding="utf-8").read()
    log = yaml.safe_load(raw)
    is_list = isinstance(log, list)
    if is_list:
        items = log
    else:
        items = log.get("issues", [])

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
            print(f"  [skip] {iid} 已是 verified")
            continue
        meta = SIGN[iid]
        it["status"] = "verified"
        it["verify_result"] = meta["verify_result"]
        it["verify_date"] = NOW
        it["fix_ref"] = meta["fix_ref"]
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

    # ---------- ③ 备份 + 原子写 ----------
    bak = LOG + ".bak_20260725_0250_cronfb67af40_sign406_407_408_open409_410_411"
    shutil.copy2(LOG, bak)

    out = yaml.safe_dump(items if is_list else log, allow_unicode=True, sort_keys=False, width=100)
    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out)
    os.replace(tmp, LOG)

    # ---------- ④ CAS 守卫: 除 3 签收 + 3 新增外, 其余逐条 md5 必须不变 ----------
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
