#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 05:2x · job 775d9893「ARS45 继续执行后继计划」
★(1) 开 ISS-273 (MECH 侧 H-1 重锚机制收口: 判决源从「域侧锚点副本」换成「落表台账最新记录」)★
★(2) 给 state/dispatch_briefs/ISS-253_mech_h1_reanchor.md 顶部加「已作废」横幅 (★防再次派过期单★)★
★**只动 2 个文件: state/issue_log.yaml (文件尾追加一块) + state/dispatch_briefs/ISS-253_*.md (顶部加横幅)★**
★**不碰真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何门禁脚本**★
★**纪律: 原文件里 note / task_brief 是多行标量 ⇒ 本脚本绝不改写它们 (改写会打断 YAML 续行)★**
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0530_main_open_iss273"
BRIEF = os.path.join(PROJ, "state", "dispatch_briefs", "ISS-273_mech_h1_anchor_single_source.md")
STALE_BRIEF = os.path.join(PROJ, "state", "dispatch_briefs", "ISS-253_mech_h1_reanchor.md")

TODAY = "2026-11-17"
IID = "ISS-273"


def q(v) -> str:
    """单行 YAML 标量 (不换行 · 强制双引号 ⇒ 不受 ': ' / 特殊字符影响)"""
    return json.dumps(v, ensure_ascii=False)


NOTE = (
    "2026-11-17 05:2x (cron 775d9893) 新开 ★**依据 = main 本轮 05:1x 本机实跑 + mech-lead ISS-253 续做复核报告**★ "
    "⇒ ★**任务书 `state/dispatch_briefs/ISS-273_mech_h1_anchor_single_source.md`**★ "
    "⇒ ★**本单要修的东西 (★一句话★): 把 C21/G5b 的【判决源】从【域侧锚点副本 MECH/HW_CROSS_REVIEW_TRIAGE.md §1 "
    "source_ledger.entries[].md5】换成【落表台账里的最新记录】**★ ⇒ ★**合法落表不再红 (收益), 而「悄悄换真源」仍然红 (代价)★★ "
    "⇒ ★**背景 (★main 本机实跑, 原样★)**: ① 网表/脚表 md5 锚点已跳 6 跳 (ISS-220 → ISS-223 → ISS-233 → ISS-243 → ISS-249 → ISS-257) "
    "⇒ 每跳 = 上游一次合法落表 ⇒ 域侧锚点当场过期 ⇒ 门禁红 ⇒ 再开一条 dispatch 单 → 人工重锚 + 人工留痕 ② 2026-11-17 05:0x 这一轮 "
    "★**这个循环白跑了一整轮**: main 派 ISS-253 (H-1 重锚) ⇒ 该单前提【已过期】 (★门禁实测 rc=0 · 23/23 · FAIL 0★; "
    "锚点现值已是第 6 跳 `e06c1dd6…`, 不是派单说的 `16ac89f7…`; 且 `issue_log` 里 ISS-253 status 已 = `verified`) "
    "⇒ ★**且派单写错了文件**: 派单写「文件 = `MECH/check_demo_struct_truth.py`」, ★**真锚点在 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 "
    "`MECH_ANCHORS` 块, 脚本只是读它** (★脚本自己注释: 「本文件 §1 只做台账/留痕, 不是判决源」★) ③ mech-lead 域内新门禁 "
    "`MECH/check_hinge_fpc_truth.py` 已改成【网表/脚表 md5 现场解析、一律不写死】⇒ 本单把同口径推到 `check_demo_struct_truth.py`★ "
    "⇒ ★**判据语义不许松**: 本闸存在的唯一理由 = 「悄悄换真源」必须红 ⇒ 改完「红」的条件从「盘上 ≠ 域侧锚点」变成「盘上 ≠ 台账最新记录」★ "
    "⇒ ★**反向用例必须加压 (★命门两条★)**: R2 (盘上 == 台账最新登记, 域侧锚点副本还是旧值 ⇒ 必须【绿】= 本单效果证明) + "
    "R4 (台账里同一文件有多条历史记录 ⇒ 必须取最新, 故意打乱顺序仍取最新 ⇒ 「取错记录 ⇒ 假绿」这条路必须堵死)★ "
    "⇒ ★**只许改 C21/G5b 里【台账管理真源取值 + 比对】那段逻辑**, 其它 21 组判据 / 16 条 FAIL 名单 / 判据阈值 / 板框四数 / "
    "板 / .kicad_pro / 网表 / 脚表 / BOM 一个字节都不许动★ ⇒ ★**SW 侧同构问题 (`SW/tools/check_demo_panel_spec.py` R6) 不在本单地界 "
    "(★不许越界写别人的域★) ⇒ main 另派**★ "
    "⇒ ★**边界**: 零落表 · 零外发 · 零实物 · 不碰 HW/ 与 SW/ · 不碰布线/布局/板框 · 不改判据阈值 · 不许替老板拍板 · 不自签 issue_log★ "
    "⇒ ★**主线口径**: 老板 2026-11-17 00:43 主线 = 绘制 PCB 图 ⇒ ★**本单不碰板, 不占「板只改一次」那一趟的任何一步 ⇒ 可派**★"
)

NEW = {
    "id": IID,
    "title": (
        "★★[主线内·MECH 侧·门禁机制收口·内部活] ★★**网表/脚表 md5 锚点已跳 6 跳 ⇒ 「一落表就红, 必人工重锚」** ★★ "
        "⇒ ★**把 C21/G5b 的判决源从【域侧锚点副本】换成【落表台账最新记录】** ★ ⇒ ★**合法落表不再红, 而「悄悄换真源」仍然红** ★ "
        "★★(★依据: main 2026-11-17 05:1x 本机实跑 + ISS-253 派单前提已过期的事故 + mech-lead 域内 `check_hinge_fpc_truth.py` "
        "已用「现场解析」口径的先例★)"
    ),
    "severity": "medium",
    "owner": "mech-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-21",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": NOTE,
    "dispatched_at": None,
}


def dump_block(d) -> str:
    lines = ["- id: %s" % d["id"]]
    for k, v in d.items():
        if k == "id":
            continue
        if v is None:
            lines.append("  %s: null" % k)
        elif isinstance(v, bool):
            lines.append("  %s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, (int, float)):
            lines.append("  %s: %s" % (k, v))
        else:
            lines.append("  %s: %s" % (k, q(v)))
    return "\n".join(lines)


def main() -> int:
    # ---- 0) 前置断言: ISS-273 不许已存在 ----
    raw = open(LOG, encoding="utf-8").read()
    if ("\n- id: %s\n" % IID) in ("\n" + raw) or raw.lstrip().startswith("- id: %s" % IID):
        print("❌ %s 已存在 ⇒ 不许重复开单" % IID)
        return 2

    # ---- 1) issue_log.yaml 尾部追加新块 ----
    shutil.copy2(LOG, BAK)
    text = raw
    if not text.endswith("\n"):
        text += "\n"
    NEW["task_brief"] = open(BRIEF, encoding="utf-8").read()
    block = dump_block(NEW)
    text += "\n" + block + "\n"
    open(LOG, "w", encoding="utf-8").write(text)

    # ---- 2) 给过期的 ISS-253 brief 加作废横幅 ----
    st = open(STALE_BRIEF, encoding="utf-8").read()
    if "【已作废 · 不要再派】" not in st:
        banner = (
            "> ★★【已作废 · 不要再派】★★ ★**2026-11-17 05:2x main 标注**★\n"
            "> 本单 (ISS-253 H-1 重锚 第 4 跳 R-05) ★**已于 2026-11-16 20:0x 落表交付**★, 之后又被 ★**ISS-259 (第 6 跳 R-06, by ISS-257)**★ 覆盖 ⇒ "
            "★**现在盘上的锚点现值 = 网表 `e06c1dd633566aa44732762c2ff99d1c` / 脚表 `287e7861a0d1007748d92d9fbecdd490`**★\n"
            "> ⇒ ★**照本单字面落地 = 把网表谎报成 ISS-249 旧版本 = 打红 + 做假绿** ★ ⇒ ★**本单已作废, 不要再派 mech-lead 重锚** ★\n"
            "> ★**另**: 本单写的「文件 = `MECH/check_demo_struct_truth.py`」★**不成立** ★ ⇒ ★**锚点在 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS` 块**, "
            "脚本只是**读**它 ⇒ ★**以后派 H-1 单请直接写锚点文件** ★\n"
            "> ★**替代任务书**: `state/dispatch_briefs/ISS-259_mech_h1_reanchor_jump6.md` (第 6 跳, 已 verified) · "
            "机制收口单 = `state/dispatch_briefs/ISS-273_mech_h1_anchor_single_source.md` (★判决源改成台账最新记录, 合法落表不再红★)\n\n"
        )
        open(STALE_BRIEF, "w", encoding="utf-8").write(banner + st)

    # ---- 3) 自检: YAML 合法 + 新单字段齐 + issue_check 通过 ----
    d2 = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d2["issues"]}
    print("issues total:", len(ids))
    it = ids.get(IID)
    if not it:
        print("❌ %s 追加失败" % IID)
        return 2
    print("  %s -> %s owner=%s severity=%s due=%s verify_by=%s" % (
        IID, it["status"], it["owner"], it["severity"], it["due"], it.get("verify_by")))
    print("  task_brief bytes =", len(it.get("task_brief") or ""))
    print("  stale brief banner =", "【已作废 · 不要再派】" in open(STALE_BRIEF, encoding="utf-8").read())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
