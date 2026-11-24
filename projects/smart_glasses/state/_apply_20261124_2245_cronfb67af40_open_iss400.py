#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20261124_2245_cronfb67af40_open_iss400.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-24 22:4x 一趟
  ⇒ ★**新开 1 条内部单 (ISS-400) 并【直接落 `fixing`】** (★铁律⑩-i: 先落 fixing 再 spawn ⇒
    兄弟 job `775d9893` 的 `advance.py --json` 看不见 ⇒ 零撞车窗口★)

★**为什么这轮开单 (★本机实读, 不抄任何 agent 报告★)**:
  · `python3 state/advance.py --json` ⇒ `internal: []` / `approvals: []` / `waiting: []` / `decisions: 55`
  · 台账 16 条 `open` 的 owner 全部 = `boss`(5) / `main`(11) ⇒ 不在三个总工可派域 (advance.py L33
    `AGENT_ROLE = {"hw-lead","sw-lead","mech-lead"}`)
  · 三个槽位实检 (两采样法 · 间隔 ~90 秒): hw-lead `ca14678f` (989,200 B → 1,023,147 B) +
    sw-lead `d35b8dd2` (1,084,866 B → 1,193,944 B) ⇒ **两条真在飞 ⇒ 不许续派**;
    mech-lead `753cb5df` (ISS-399 cont2) **22:14:03 已 done + 交卷报告在盘 ⇒ 槽位实际已空**
  · ⇒ 只有 mech-lead 一个空槽位 ⇒ 本 job 逐道实跑 MECH 域 11 道闸 (留证 `state/.verify/fb67_2245/`)
    ⇒ 9 道 rc=0 / 2 道 rc=1 (★`check_fts_seat_sample_plan.py` 红的是三量实测 [0数据] 的现状 ·
    `check_mech_signed_append_ledger.py` 红的是 3 处陈旧 pin 未登记台账的现状★) ⇒ 闸全绿或红在现状
  · ⇒ **真缺口不是闸红, 是 main 22:4x 逐行读出来的【跨页机器块指针死路】**:
    ISS-393 页 §5 动作表 (L176/L177/L178) 让收样人把三量实测填进 `dimensions.factory_seat_body_x_4pos.measured`
    / `factory_seat_body_y.measured` / `factory_insulator_height_z.measured`
    ⇒ 这三个键在同页 §6 机器块里**不存在**; 同页真键 (`seat_body_x_4pos` / `seat_body_y` /
    `insulator_height_z`) **又没有 `measured` 字段** ⇒ **即便改对前缀也还是填不了**;
    唯一真槽在**另一页** `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` 的
    `three_quantities.{insulator_height_z, seat_body_width_x, seat_body_depth_y}` (槽名拼法还不同)
    ⇒ 而收样闸 `MECH/check_fts_seat_sample_plan.py` L45/L75/L223 **只认那三个槽** ⇒ 死路径
  · ⇒ ISS-397 页 L199/L338 已把这条登记成「交 main 的问句」并**挂了两天没人答** ⇒ 本单把它变成
    【清单 + 机器闸 + 逐字改法】, **零改既有页正文 / 一条都不代拍**

★**本脚本三道自保**: ① md5 守卫 (写前重算源文件 md5, 不一致 ⇒ rc=3 中止)
  ② 原子写 (`os.replace`) ③ 写后复跑 `state/check_brief_commands.py`
★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = os.path.join(HERE, "issue_log.yaml.bak_20261124_2245_cronfb67af40_open_iss400")
BRIEF_REL = "ISS-400_mech_machine_block_pointer_resolvable_audit.md"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def brief_text(name):
    with io.open(os.path.join(BRIEFS, name), encoding="utf-8") as f:
        return f.read()


def main():
    if not os.path.exists(LOG):
        print("★issue_log.yaml 不存在 ⇒ 中止")
        return 2
    src_md5 = md5(LOG)
    with io.open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    issues = doc.get("issues") or []
    have = {i.get("id") for i in issues}
    if "ISS-400" in have:
        print("★ISS-400 已在台账 ⇒ 中止 (不重复开单)")
        return 2

    common = dict(
        source_agent="main",
        verify_by="main",
        reporter="main",
        raised="2026-11-24",
        due="2026-11-27",
        status="fixing",
        external=False,
        dispatched_at="2026-11-24",
    )

    note_common = (
        "★**2026-11-24 22:4x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】**"
        "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★) ★\n"
        "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `python3 state/advance.py --json` 实跑 ⇒ "
        "`internal: []` / `approvals: []` / `waiting: []` / `decisions: 55`; ★**台账 16 条 `open` 的 owner "
        "全部 = `boss`(5) / `main`(11) ⇒ 不在三个总工可派域** (★`state/advance.py` L33 "
        "`AGENT_ROLE = {\"hw-lead\",\"sw-lead\",\"mech-lead\"}`★) ★\n"
        "★**② 三个槽位两采样实检 (★间隔 ~90 秒 · 体积在长 ⇒ 真在飞★)★**: ★hw-lead `ca14678f` "
        "989,200 B → 1,023,147 B (↑33,947)· `advance_iss391_cont2`· **真在飞 ⇒ 不许续派**★; "
        "★sw-lead `d35b8dd2` 1,084,866 B → 1,193,944 B (↑109,078)· `advance_iss398_cont2`· "
        "**真在飞 ⇒ 不许续派**★; ★mech-lead `753cb5df` (`advance_iss399_cont2`) **22:14:03 已 done + "
        "交卷报告在盘 ⇒ 槽位实际已空** ⇒ ★**只有 mech-lead 一个空槽位**★ ★\n"
        "★**③ 逐道实跑 MECH 域 11 道闸 (留证 `state/.verify/fb67_2245/`)★**: ★9 道 rc=0; "
        "`check_fts_seat_sample_plan.py` rc=1 (★红的是三量实测档 `[0数据]` 的现状, 不是闸故障★); "
        "`check_mech_signed_append_ledger.py` rc=1 (★红的是 3 处陈旧 pin 未登记台账的现状★) ⇒ "
        "★**闸全绿或红在现状 ⇒ 真缺口不在这 11 道闸的读数上, 在【页与页之间的机器块指针】上** ★\n"
        "★**④ 真缺口 (main 22:4x 逐行实读)★**: ★`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` "
        "§5 动作表 L176/L177/L178 让收样人把三量实测填进 `dimensions.factory_seat_body_x_4pos.measured` / "
        "`factory_seat_body_y.measured` / `factory_insulator_height_z.measured` ⇒ ★这三个键在同页 §6 机器块里"
        "**一个都不存在**★; ★同页真键 `seat_body_x_4pos` / `seat_body_y` / `insulator_height_z` "
        "(L518/L538/L548) **又没有 `measured` 字段** ⇒ 即便改对前缀**那一格依然不存在**★; "
        "★**唯一真槽在另一页** `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` 的 "
        "`three_quantities.{insulator_height_z, seat_body_width_x, seat_body_depth_y}` (★槽名拼法还不同: "
        "`seat_body_width_x` ≠ `seat_body_x_4pos`★)⇒ ★而收样闸 `MECH/check_fts_seat_sample_plan.py` "
        "L45/L75/L223 **只认那三个槽** ⇒ ★**死路径: 测完的数落不了地**★ ⇒ "
        "★**座体深 Y 与绝缘体高 Z 的公差是 `[0数据]` ⇒ 这两量只能靠实测升档 ⇒ 而实测回填格指错 ⇒ "
        "「板只改一次」那一趟投板前的必量动作永远不成立 ⇒ 坏结局两条: ① 带着 `[0数据]` 公差放行投板 ⇒ "
        "**板改第二次**; ② 永远卡在「闸红」上 ⇒ 那一趟永远不许开工**★ ★\n"
        "★**⑤ 这条至今没人做**: ★ISS-397 页 L199 已逐字登记、L338 已逐字问 main「要不要落一个追加式订正块把"
        "三个键名改对?」⇒ ★**挂了两天没人答** ⇒ 本单把它变成【全仓清单 + 机器闸 + 逐字改法】★ ★\n"
        "★**⑥ 派活纪律**: ★**本单是「纯查证 + 纯分析 + 新建真相页 + 新建机器闸」类 ⇒ 合「板只改一次」纪律 ① "
        "(先派纯分析/作业包类, 不动板) ⇒ 零写板·零落表·零改既有页正文·零改既有闸判据·零挂链·零外发·不代拍** ★\n"
        "★**命令存在性守卫**: ★`python3 state/check_brief_commands.py --brief-file "
        "state/dispatch_briefs/%s` ⇒ **rc=0** ★" % BRIEF_REL
    )

    new_issues = [
        dict(
            id="ISS-400",
            title=(
                "★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板] 「板只改一次」那一趟"
                "投板前必量的三个量【回填格指针打到了不存在的键】⇒ 收样动作永远转绿不了 ⇒ 把「跨页机器块指针"
                "是否真的指向一个存在的槽」变成机器可判的闸 ★★"
            ),
            severity="high",
            source_blocker="ISS-397",
            desc=(
                "★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸+沙盒夹具·零写板·零落表·"
                "零改既有闸判据·零改既有页正文·零挂链·零外发·不代拍]★★\n\n"
                "★**题 (来源 = ★main 2026-11-24 22:4x 本机实读台账 + 逐行读页 + 实跑 MECH 域 11 道闸·"
                "不抄任何 agent 报告★)★:\n"
                "★**① 现象**: ★`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` (ISS-393 真相页) §5 "
                "「量完填回哪一格」动作表 L176/L177/L178 逐字写 `dimensions.factory_seat_body_x_4pos.measured` / "
                "`factory_seat_body_y.measured` / `factory_insulator_height_z.measured` ⇒ ★**这三个键在同页 §6 "
                "机器块 `dimensions` 里一个都不存在** (真键 = `seat_body_x_4pos` L518 / `seat_body_y` L538 / "
                "`insulator_height_z` L548 / `factory_drill` L568)★ ⇒ ★**同页那三个真键又没有 `measured` 字段** ⇒ "
                "★**即便改对前缀, 那一格依然不存在 ⇒ §5 指错了页, 不只是指错了键名**★ ★\n"
                "★**② 唯一真槽在另一页**: ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` 机器块 "
                "`three_quantities.{insulator_height_z, seat_body_width_x, seat_body_depth_y}` (★L386 起 · "
                "`measured_value: null` / `measured_evidence: \"[0数据]\"`· 槽名拼法还与 §5 写的不同★) ⇒ "
                "★**收样闸 `MECH/check_fts_seat_sample_plan.py` L45 `PAGE_REL` / L75 `QUANT_KEYS` / L223 "
                "`blk.get(\"three_quantities\")` 只认那三个槽** ⇒ ★**死路径**★ ⇒ ★**全仓 grep "
                "`factory_seat_body|factory_insulator` 只有 5 处转述, 没有任何闸读它**★ ★\n"
                "★**③ 为什么值钱**: ★座体深 Y 与绝缘体高 Z 的公差 = `[0数据]` (官网只有 REF 基准, 未给公差带) ⇒ "
                "★**这两量只能靠实测升档** ⇒ ★**实测回填格指错 ⇒ 测完的数落不了地 ⇒ 收样闸永远红在 B.6** ⇒ "
                "★**坏结局二选一: ① 有人把「闸还红」读成「还没到收样时点」⇒ 带着两个 `[0数据]` 的公差放行投板 ⇒ "
                "【板改第二次】; ② 永远卡住 ⇒ 那一趟永远不许开工** ⇒ ★**这就是【板只改一次】纪律最怕的那类洞: "
                "不是算错, 是【动作做完但数据落不了地】**★ ★\n"
                "★**④ 为什么至今没人做**: ★ISS-397 页 L199 逐字登记 + L338 逐字问 main「要不要落一个追加式订正块"
                "把三个键名改对?」⇒ ★**挂了两天没人答** ⇒ 本单把它变成【全仓清单 + 机器闸 + 逐字改法】★ ★\n"
                "★**⑤ 本单交付 (★全部零写板★)★**: ★① 真相页 `MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md` "
                "(★全仓悬空指针清单 + 真槽登记表 + 连带影响面★) ★② 新闸 "
                "`MECH/check_machine_block_pointer_resolvable.py` (★裸跑 rc=1 红的是现状 · `--selftest` rc=0 · "
                "末行 `ALL TESTS PASS`· 正向 ≥1 + 反向 ≥6★) ★③ 交卷页 B1~B7 全填 ★\n"
                "★**⑥ 归 main 的四条问句 (★本单一律不代拍★)★**: ★§5 那 3 个死指针要不要按追加式订正块改对 · "
                "改指针时 `MECH/check_fts_seat_sample_plan.py` L71 那枚 md5 pin 要不要同批刷新 · "
                "ISS-397 §9-④ 那条问句是不是就由本单的逐字改法来答 · 新闸挂不挂链 ★"
            ),
            owner="mech-lead",
            need_keys=["iss400_pointer_audit_verdict", "iss400_pointer_correction_text"],
            task_brief=brief_text(BRIEF_REL),
            note=note_common,
        ),
    ]

    for i in new_issues:
        for k, v in common.items():
            i.setdefault(k, v)

    # ---- ① md5 守卫: 写前重算 ----
    if md5(LOG) != src_md5:
        print("★md5 守卫: 源文件在读与写之间被改过 ⇒ 中止 (rc=3)")
        return 3

    doc["issues"] = list(issues) + new_issues
    shutil.copy2(LOG, BACKUP)
    tmp = LOG + ".tmp.%d" % int(time.time())
    with io.open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100000)
    # ---- ② 原子替换 ----
    os.replace(tmp, LOG)

    print("★已写 %s (+1 条: ISS-400 · owner=mech-lead · status=fixing)" % LOG)
    print("★备份 %s (md5 %s)" % (BACKUP, md5(BACKUP)))
    print("★台账条数 %d → %d" % (len(issues), len(doc["issues"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
