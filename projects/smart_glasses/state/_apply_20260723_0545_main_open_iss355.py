#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20260723_0545_main_open_iss355.py —— main 开 ISS-355 (sw-lead · 转换脚本迁主路线)"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

TITLE = ("★★[★模型链·实现侧·纯脚本·零写板] ★★【ISS-353 已签收 ⇒ 口径清了, 但【实现】没改: "
         "`SW/tools/rk3572_model_rebuild.sh` (L13/L86/L136) 与 `SW/RKNN_BENCH.md` §5 仍是 toolkit2 + "
         "`target_platform='rk3576'` ⇒ 任何人按现脚本重跑, 拿到的仍是 rk3576-target 产物 ⇒ "
         "主路线 (rknn3-toolkit 1.2.0 + rk3572) 还没落到脚本上 ⇒ 本单 = 把主路线落到脚本上 + 新建机器闸钉住】★★ "
         "★**口径清了 ≠ 实现改了 ⇒ 这是 ISS-353 §B7 残留表里的 `iss353_need_followup_convert_script_rk3572` "
         "(登记为 to=main · 等 main 确认优先级) ⇒ 本单就是它**★")

DESC = ("★**main 2026-11-23 05:4x 本机实读 (不抄 agent 报告)★** ⇒ ★**① 上游**: ISS-353 已由 main 签收 (★33 条验收线全绿 + "
        "自测 8/8·机器判决★) ⇒ 口径真值已钉死: ★**toolkit2 (2.3.2/2.5.0) 不支持 rk3572 target [官网]+[实测] ⇒ 转换链要走 "
        "rknn3-toolkit 1.2.0 (其 `config(target_platform='rk3572')` rc=0 [实测], 转换 rc=0, 产物逐字节可复现)**★ ⇒ "
        "★**② 残留**: 全仓 16 条旧结论已由 main 一键补丁清掉 15 条 (文档类) · 剩 2 条在 `hw.yaml` (hw-lead 地界) ⇒ 但 "
        "`SW/tools/rk3572_model_rebuild.sh` 的默认路线**仍是旧链** ⇒ 口径与实现脱节 ⇒ 任何按脚本重跑的人都会拿到 rk3576-target 产物 "
        "⇒ ★**③ 一个必须点名的坑 (ISS-353 已点出)**: rknn3-toolkit 1.2.0 的产物是 **`.rknn` + `.weight` 两件套** ⇒ "
        "**只拷 `.rknn` 一定失败** ⇒ 脚本的拷贝段必须两件套一起处理 ⇒ ★**④ 为什么现在做**: demo 路线的模型链要能一条命令重建 "
        "(板到手时的验收也要用同一套产物) ⇒ 默认路线必须先落到脚本上 ⇒ ★**⑤ 边界**: 零写板 (板 md5 "
        "`611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 必须逐字节不变) · 零落表 · 零外发 · 零采购 · "
        "不替老板拍板 · 不新增拍板项 · 只写 SW/ 域 + 交卷页 + logs/iss355/ + sw.yaml 分片 ★")

BRIEF = ("★**题**: ISS-353 交卷页 §B7 残留表第 1 行 (`iss353_need_followup_convert_script_rk3572`) ⇒ "
         "★**口径清了 ≠ 实现改了**: `SW/tools/rk3572_model_rebuild.sh` (L13/L86/L136) 与 `SW/RKNN_BENCH.md` §5 仍是 "
         "toolkit2 + `target_platform='rk3576'` ⇒ **主路线 (rknn3-toolkit 1.2.0 + rk3572) 还没落到脚本上** ⇒ "
         "★**本单只做 3 件 (不许扩项)**: ① `rk3572_model_rebuild.sh` 迁主路线 (**默认路线必须改, 不许只加注释**; 旧链保留为次要路线①; "
         "**`.rknn` + `.weight` 两件套的拷贝逻辑必须处理** —— 只拷 `.rknn` 一定失败) ② `SW/RKNN_BENCH.md` §5 追加式订正 "
         "(老字别删) ③ 新建只读机器闸 (扫全仓: 凡仍把「用 rk3576 转」当**当下执行口径**的 ⇒ 逐条点名 + 输出带名单 + rc=1; "
         "断言脚本默认 target = rk3572 + rknn3-toolkit 1.2.0; 断言两件套拷贝在位; **必须带 `--selftest` 反向用例**; 末行 ALL TESTS PASS) ★ "
         "★**必跑**: `python3 state/merge.py` (rc=0) && `python3 state/gate_check.py` (★Q1 必须 18/18★) && "
         "`md5sum HW/PCB/demo_mainboard.kicad_pcb` (必须 611b869e13518c3c023fb178f91a0075) ★ "
         "★**任务书全文**: `state/dispatch_briefs/ISS-355_sw_convert_script_rk3572.md` "
         "(★`python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-355_sw_convert_script_rk3572.md` ⇒ rc=0★) ★")

NOTE = ("★★2026-11-23 · main 开单 (★项目总工 main★) ★★ ★**开单依据**: ISS-353 交卷页 §B7 残留表自列的 followup "
        "(`iss353_need_followup_convert_script_rk3572` · 登记为 to=main ⇒ 等 main 确认优先级) ⇒ main 确认优先级 = "
        "**排在板那一趟之前做** (★模型链是 demo 路线的主链, 且改动只碰 SW 域脚本·零写板·不占老板拍板面★) ★ "
        "★**状态落 open (不落 fixing)**: 派活由队列 job (fb67af40) 执行 ⇒ 落 fixing 会造成「没人跑的僵尸 fixing」★ ⇒ "
        "★**待派**: owner = sw-lead (★sw-lead 的 ISS-353 已交卷, 槽位空出来了★) ★ "
        "★**本单不占老板拍板面** (ISS-155 台账标签是另一件事, 交 main 裁) ★")

ENTRY = {
    "id": "ISS-355",
    "title": TITLE,
    "severity": "medium",
    "source_blocker": "ISS-353",
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
    if "\n- id: ISS-355" in src:
        print("★ISS-355 已在台账 ⇒ 不重复开单")
        return 0
    chunk = yaml.safe_dump([ENTRY], allow_unicode=True, sort_keys=False, width=200)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    shutil.copy2(LOG, LOG + ".bak_%s_main_open_iss355" % STAMP)
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
    print("台账条数 = %d · ISS-355 在盘 = %s · 零重复 id = %s"
          % (len(ids), "ISS-355" in ids, len(ids) == len(set(ids))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
