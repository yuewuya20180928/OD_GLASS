#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20260723_0825_main_open_iss357.py —— main 开 ISS-357 (sw-lead · SW 域 needs 144 条四分类处置)"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BRIEF_FILE = os.path.join(PROJ, "state/dispatch_briefs/ISS-357_sw_open_req_triage.md")
STAMP = time.strftime("%Y%m%d_%H%M")

TITLE = ("★★[主线内·SW 侧·需求闭环类·内部活] ★★【SW 域 needs 144 条四分类处置 (waiting_on 空 118 / "
         "to=hw-lead 17 / to=mech-lead 2 / agent 4 / boss 12 / vendor 8) ⇒ 把机检缺口清单那条「98 条没人答」+ "
         "「8 条外发依赖挂着」两笔老账一次清掉】★★ ⇒ ★**与 MECH 域同型单 ISS-313 (verified) 同一口径** ★")

DESC = ("★**main 2026-11-23 08:1x~08:2x 本机实读 (不抄 agent 报告)★** ⇒ ★**① 机检**: `python3 state/gate_check.py` (rc=0) ⇒ "
        "缺口清单 3 条: hw-lead 179 / **sw-lead 98** / mech-lead 76 条需求确实还没人答 (★口径: "
        "`real_open = needs_total − needs_answered_incoming − needs_closable_unregistered − needs_waiting_external`★) ⇒ "
        "★**② SW 域自己的账** (`state/fragments/sw.yaml` 实读): `needs_from` = 144 条 ⇒ to=main&waiting_on空 99 · "
        "to=hw-lead&空 17 · to=main&boss 12 · **to=vendor&vendor 8** · to=main&agent 4 · to=mech-lead&空 2 · to=main&sw-lead 2 ⇒ "
        "★**③ 那 8 条 vendor 是【外发口径违规】**: 原文写着「走 main 发第二轮邮件 / 经 main 转达 / 请项目总工并进第二轮邮件」⇒ "
        "★违反老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信, 全靠自己查资料」⇒ 其中 `model_license_yolov5sim` 本地早已查完 "
        "(AGPL-3.0, 证据链 7 环, 见 `SW/MODEL_LICENSE.md` §1.2) 竟还挂在 vendor 上 ⇒ ★**④ 陈旧漂移已现**: 12 条 boss 类里 "
        "`demo_od_p0_4_panel_init_code` 自己标了「已结 (ISS-212)」却仍挂着 need ⇒ ★**⑤ 为什么现在做**: 主线 = 绘制 PCB 图 "
        "(老板 11-17 00:43) ⇒ 板只改一次 ⇒ SW 侧待答条目里的「板框/板厚/层数/镜腿宽度/检修口净空/重量预算/位号改名/布线 45→0/"
        "Gerber 投产包重出/Q3 存储分档」相关项必须先清出来当板那一趟的输入 ⇒ ★**⑥ 边界**: 零写板 (板 md5 "
        "`611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 必须逐字节不变) · 零落表 · 零改闸 · "
        "零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log · 只写 SW/ 域新件 + 交卷页 + logs/iss357/ + sw.yaml 分片 ★")

NOTE = ("★★2026-11-23 08:2x · cron fb67af40 (ARS45 队列自动派活) 开单并派出 (★项目总工 main★) ★★ ★**开单依据**: "
        "★**① 队列真空**: `python3 state/advance.py --json` 的 internal = 0 条 (三个总工名下 open 全为 0) ⇒ "
        "sw-lead 名额空着; ★**② 但内部待办其实没断线 —— 断线的那一截在 needs 里**: `state/gate_check.py` 缺口清单白纸黑字 "
        "「sw-lead: 98 条需求确实还没人答」⇒ ★**这才是本 job 「让内部待办不断线」的真对象** ⇒ ★**③ 有同型先例**: "
        "ISS-313 (mech-lead · MECH 域 needs 184 条四分类处置) = verified ⇒ MECH 分片 184→139 条、vendor 10→0、jbd 6→0 ⇒ "
        "★**SW 域同一件事还没做 ⇒ 本单照抄那个已验证的口径 / 交卷物结构 / 对账要求** ★ ★**④ 老板外发口径的直接落点**: "
        "那 8 条 vendor 的原文仍在喊「发第二轮邮件」⇒ 必须改成【自己网上查 + 证据等级 + 降级方案】 ⇒ 这正是老板 "
        "2026-11-11 19:31 + 2026-11-12 02:02 的口径 ★ ★**⑤ 不占老板拍板面** (12 条 boss 类只整理成 need key + 决策码, 不代拍) ★ "
        "★★**派活顺序**: ★先 `advance.py --apply --only ISS-357` 落 fixing ⇒ 再 spawn (★关掉下一轮 cron 重复派的窗口★) ★★")

BRIEF = open(BRIEF_FILE, encoding="utf-8").read()

ENTRY = {
    "id": "ISS-357",
    "title": TITLE,
    "severity": "high",
    "source_blocker": "ISS-270",
    "source_agent": "main",
    "desc": DESC,
    "owner": "sw-lead",
    "reporter": "main",
    "raised": "2026-11-23",
    "due": "2026-11-25",
    "status": "open",
    "external": "false",
    "task_brief": BRIEF,
    "dispatched_at": None,
    "verify_by": "main",
    "verify_result": None,
    "note": NOTE,
}


def main():
    src = open(LOG, encoding="utf-8").read()
    if "\n- id: ISS-357" in src:
        print("★ISS-357 已在台账 ⇒ 不重复开单")
        return 0
    chunk = yaml.safe_dump([ENTRY], allow_unicode=True, sort_keys=False, width=200)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    shutil.copy2(LOG, LOG + ".bak_%s_main_open_iss357" % STAMP)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src + chunk)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)
    if isinstance(items, dict):
        items = list(items.values())
    ids = [i.get("id") for i in items]
    print("台账条数 = %d · ISS-357 在盘 = %s · 零重复 id = %s"
          % (len(ids), "ISS-357" in ids, len(ids) == len(set(ids))))
    print("brief = %d B (台账 task_brief 与文件同内容 = %s)"
          % (len(BRIEF), BRIEF == next(i for i in items if i["id"] == "ISS-357")["task_brief"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
