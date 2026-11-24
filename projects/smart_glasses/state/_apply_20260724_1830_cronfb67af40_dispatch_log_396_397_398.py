#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20260724_1830_cronfb67af40_dispatch_log_396_397_398.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-24 18:2x 一趟
  ⇒ 往 `state/dispatch_log.yaml` 追加 3 条派活记录 (★ISS-396 / ISS-397 / ISS-398★)
★**自保**: ① md5 守卫 (写前重算源文件 md5, 不一致 ⇒ rc=3 中止) ② 原子写 (`os.replace`) ③ 写后复算条数
★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改 PROJECT_TRACKER §0 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "dispatch_log.yaml")
BACKUP = os.path.join(HERE, "dispatch_log.yaml.bak_20261124_1830_cronfb67af40_396_397_398")

JOB = (
    "cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 18:2x · ★**先落 fixing 再 spawn (★铁律⑩-i ⇒ 零撞车窗口★) "
    "· ★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file` 三条全 rc=0** ★ "
    "· ★**纯分析 / 登记落盘 / 新建真相页 + 新建机器闸类 (零写板·零落表·零改既有闸判据·零改已签收页正文·零挂链·零外发·不代拍) "
    "⇒ 合「板只改一次」纪律 ①** ★ · ★**开单依据 = 本 job 本机实读 + 实跑: `advance.py --json` ⇒ internal [] "
    "(三个总工名下各占 fixing 在飞单) ⇒ 逐条实检三条最新会话 (ISS-395 16:45 交卷页 / ISS-392 15:15 / ISS-393 cont1 16:46) "
    "⇒ 三个槽位实际已空 ⇒ 本 job 逐道实跑板侧 10 道 + 结构侧 9 道 + SW 侧 8 道 ⇒ **唯一真红 = "
    "`HW/check_fts_land_drill_same_batch.py` (rc=1 · 4/7 · D1/D2/D3 红)** ⇒ 本轮 3 条 = 三处缺口各一条纯分析/登记/建闸类活** ★"
)

ENTRIES = [
    dict(
        issue="ISS-396",
        agent="hw-lead",
        at="2026-11-24 18:2x",
        brief=(
            "★★[新开] 「板只改一次」那一趟的 FTS 排针【改孔 `0.65 → 0.71`】这条板侧动作【还没进作业包 §0.2 ③ / 预检清单 B33】"
            "⇒ 把 ISS-391 交回的 §4 登记项一次性落到位 ⇒ 让 `HW/check_fts_land_drill_same_batch.py` 由 4/7 转 7/7 "
            "★★★★**登记落盘(改文档 + 改生成器) + 新建闸 · 零写板 · 零落表 · 零改既有闸判据 · 零改已签收页正文 · 零挂链 · 零外发 · 不代拍** "
            "⇒ 合「板只改一次」纪律 ①★★"
        ),
        brief_file="state/dispatch_briefs/ISS-396_hw_fts_drill_registration_landing.md",
        job=JOB,
        status_note=(
            "★台账 status 由新建直接落 `fixing` (★不是 open★) ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再给该 agent "
            "派活 ⇒ 零撞车窗口★"
        ),
        task_name="queue_iss396",
        dispatched_at="2026-11-24 18:2x",
        redispatch_zombie=False,
        carried_over_from=(
            "★**开单依据 = 本 job 本机实跑 (18:1x)**: `python3 HW/check_fts_land_drill_same_batch.py` ⇒ rc=1 · 4/7 绿 · "
            "D1/D2/D3 红 (留证 `state/.verify/fb67_1815/check_fts_land_drill_same_batch.py.log`) ⇒ 「落 FTS 要改孔 0.65→0.71」"
            "这条板侧动作不在那一趟的清单上 ⇒ 不在清单 = 没人做 = 投板后排针插不进 ⇒ 【板改两次】· 权威登记单 = "
            "`HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` §4 (5+1 条) ⇒ 本单 = 落到位, 不另写口径 ★"
        ),
    ),
    dict(
        issue="ISS-397",
        agent="mech-lead",
        at="2026-11-24 18:2x",
        brief=(
            "★★[新开] 座体三量 (绝缘体高 / 外形宽 / 外形深) 现在是 `[0数据]` ⇒ 把「板只改一次」那一趟投板前的"
            "【单板样 + 卡尺量三量】这条降级做成可执行收样作业包 + 机器闸 "
            "★★★★**纯查证 + 新建真相页 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · 零挂链 · 零外发 · 不代拍** "
            "⇒ 合「板只改一次」纪律 ①★★"
        ),
        brief_file="state/dispatch_briefs/ISS-397_mech_seat_sample_measure_plan.md",
        job=JOB,
        status_note=(
            "★台账 status 由新建直接落 `fixing` (★不是 open★) ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再给该 agent "
            "派活 ⇒ 零撞车窗口★"
        ),
        task_name="queue_iss397",
        dispatched_at="2026-11-24 18:2x",
        redispatch_zombie=False,
        carried_over_from=(
            "★**开单依据 = 本 job 本机实读台账 + 三份已交卷页**: ① 三量 = `[0数据]` (`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` · "
            "`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md`) ② 降级方案 D2 = 座体外形双轨, **归属 mech-lead**, "
            "必须与「板只改一次」同批 (出处 `HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md` §B5 N7) "
            "③ 收样排期 = 要 main 回答 (`state/fragments/mech.yaml` 的 `iss393-n8`) ⇒ 本单只把「怎么做」做成作业包, 排期交 main 拍 ★"
        ),
    ),
    dict(
        issue="ISS-398",
        agent="sw-lead",
        at="2026-11-24 18:2x",
        brief=(
            "★★[新开] 第三道病闸 `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` 实测 **0/7** ⇒ 差值型自测在"
            "【基线漂移】时全灭 ⇒ 把夹具改成基线无关型 + 交出 `SW_MD5` 基线重锚的逐字补丁 (不代拍) "
            "★★★★**纯分析 + 改【自测夹具】 + 出补丁 · 零写板 · 零落表 · 零改判据 · 零挂链 · 零外发 · 不代拍** "
            "⇒ 合「板只改一次」纪律 ①★★"
        ),
        brief_file="state/dispatch_briefs/ISS-398_sw_ref_reach_v2_selftest_baseline_independent.md",
        job=JOB,
        status_note=(
            "★台账 status 由新建直接落 `fixing` (★不是 open★) ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再给该 agent "
            "派活 ⇒ 零撞车窗口★"
        ),
        task_name="queue_iss398",
        dispatched_at="2026-11-24 18:2x",
        redispatch_zombie=False,
        carried_over_from=(
            "★**开单依据 = 本 job 本机实跑 (18:2x)**: `python3 SW/tools/check_sw_ref_reachability_v2.py --selftest` ⇒ "
            "反向用例 0/7 · RC-5/RC-6/RC-7 三条全灭 ⇒ 根因 = 三条都断言「破坏前必须 rc=0」而破坏前实测 rc=1 "
            "(红项逐字: 新增真隐患:SW_MD5, 真隐患 4 > 基线 3) ⇒ 差值型自测在基线漂移时全灭 ⇒ ★**sw-lead 自己在 "
            "`iss392-n3` 里点名「要改已签收件 v2 (本单零改, 要 main 派单)」⇒ 这一单就是 main 的派单** ★"
        ),
    ),
]


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    if not os.path.exists(LOG):
        print("★dispatch_log.yaml 不存在 ⇒ 中止")
        return 2
    src_md5 = md5(LOG)
    with io.open(LOG, encoding="utf-8") as f:
        rows = yaml.safe_load(f) or []
    if not isinstance(rows, list):
        print("★dispatch_log.yaml 不是 list ⇒ 中止")
        return 2
    have = {r.get("issue") for r in rows}
    for e in ENTRIES:
        if e["issue"] in have:
            print("★%s 已在派活台账 ⇒ 中止 (不重复派)" % e["issue"])
            return 2
    if md5(LOG) != src_md5:
        print("★md5 守卫: 源文件在读与写之间被改过 ⇒ 中止 (rc=3)")
        return 3
    shutil.copy2(LOG, BACKUP)
    tmp = LOG + ".tmp.%d" % int(time.time())
    with io.open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(list(rows) + ENTRIES, f, allow_unicode=True, sort_keys=False, width=100000)
    os.replace(tmp, LOG)
    print("★已写 %s (+%d 条: ISS-396 / ISS-397 / ISS-398)" % (LOG, len(ENTRIES)))
    print("★备份 %s (md5 %s)" % (BACKUP, md5(BACKUP)))
    print("★条数 %d → %d" % (len(rows), len(rows) + len(ENTRIES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
