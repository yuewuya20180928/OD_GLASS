#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 00:5x · job 775d9893「ARS45 继续执行后继计划」
★(1) 给三条已交卷的子单签 verified (ISS-258 / ISS-259 / ISS-260)★
★(2) 开三条主线内的新单 (ISS-262 hw-lead / ISS-263 sw-lead / ISS-264 mech-lead)★
★**只动 state/issue_log.yaml 一个文件 · 不碰真源 / 分片 / 决策页 / PROJECT_TRACKER§0 / 板 / 网表★**
★**纪律: 原文件里 note / task_brief / desc 是多行标量 ⇒ 本脚本【绝不改写它们】(改写会打断 YAML 续行)★
★只做: ①单行键 status / fix_ref / verify_* 的就地替换 ②块尾追加新键 ③文件尾追加新块★**
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0050_main_verify3_open3"

TODAY = "2026-11-17"


def q(v) -> str:
    """单行 YAML 标量 (不换行 · 强制双引号 ⇒ 不受 ": " / 特殊字符影响)"""
    return json.dumps(v, ensure_ascii=False)


VERIFY = {
    "ISS-258": {
        "fix_ref": ("HANDOFF/2026-11-16_sw-lead_ISS258_H1重锚第6跳.md · "
                    "SW/SW_MD5_BASELINE_LEDGER.md §1 (ISS-257 两锚点) + §3 R-09"),
        "verify_note": (
            "★**main 2026-11-17 00:3x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
            "`SW/tools/check_demo_panel_spec.py` ⇒ rc=0 (R1~R7 全过) · `--selftest` ⇒ rc=0 (16/16) · "
            "`SW/tools/timing_check.py` ⇒ rc=0 (SELFTEST 71/71) · "
            "台账 §1 两条锚点 = ISS-257 (网表 e06c1dd6… / 脚表 287e7861…) + §3 R-09 行在盘 ⇒ "
            "只重锚 + 留痕, 判据逻辑 0 改动 ⇒ 落 verified ★"
        ),
    },
    "ISS-259": {
        "fix_ref": ("HANDOFF/2026-11-16_mech-lead_ISS259_H1重锚第6跳.md · "
                    "MECH/HW_CROSS_REVIEW_TRIAGE.md §1 (ISS-257 两锚点) + §3.1 R-06"),
        "verify_note": (
            "★**main 2026-11-17 00:3x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
            "`MECH/check_demo_struct_truth.py` ⇒ rc=0 (23/23 · FAIL 0) · `--selftest` ⇒ rc=0 (14/14 · 一条没删) · "
            "§1 两锚点 = ISS-257 (网表 e06c1dd6… / 脚表 287e7861…) + §3.1 R-06 行在盘 ⇒ "
            "G5b/C21 只重锚未改判据 ⇒ 落 verified ★"
        ),
    },
    "ISS-260": {
        "fix_ref": ("HANDOFF/2026-11-16_hw-lead_ISS260_V2落表路径修复与A3冲突.md · "
                    "state/land_v_values.py (V-2 路径修复 + --selftest 11 条) · HW/ISS260_acceptance_rc.log"),
        "verify_note": (
            "★**main 2026-11-17 00:3x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
            "`--decision V-2=1` ⇒ rc=0 · `--decision V-3=E` ⇒ rc=0 · `--decision V-4=680` ⇒ rc=0 · "
            "`--decision V-2=2` ⇒ rc=2 (打回得住) · `--selftest` ⇒ rc=0 (11/11) · "
            "受保护 5 件 md5 逐字节不变 (网表 e06c1dd6… / 脚表 287e7861… / BOM 94642d07… / 板 611b869e… / .kicad_pro 3e504d2b…) ⇒ 落 verified ★ | "
            "★**本单给 main 的两条订正 (★已收进决策页 §A-补8, main 00:6x 落★)**: "
            "①「A1+A2+A3 一并拍 ⇒ 一条命令 ⇒ 15 条一次落」★**实测错了**★ ⇒ "
            "**网表侧只能转绿 14 条 (V-3 13 + V-4 1) + 4 条等板那一趟 (R4×2 + R9 + R3)** ★; "
            "② W-1 拆成 W-1a / W-1b / W-1c 三个小问分别拍 ★"
        ),
    },
}

NEW = [
    {
        "id": "ISS-262",
        "title": ("★★[主线内·原理图/网表侧·落表防假绿·内部活] ★★★**落表链没有「行号漂移」判据 ⇒ V-3 落表 (删 3 行 DNP) 会让所有行号锚点 -3 而门禁照样绿** ★★"
                  "(★依据: hw-lead 自己的 need `iss230_row_shift_false_green`「V-2 落表后有 4 条锚点换了行照样绿, 门禁不会提醒」★ + ISS-249 交卷单 §B4「行号漂移撞车 1 处」★) "
                  "⇒ ★**给落表器/门禁加行号锚点断言 (漂移必报 + 内容变必红) + 出 V-3/V-4 同批落表次序与重基线清单** ★"),
        "severity": "high",
        "source_blocker": "ISS-160",
        "source_agent": "main",
        "desc": ("★main 2026-11-17 00:3x 本机实跑 (★不抄交卷报告★): ISS-260 的落表器三条干跑全 rc=0 (`V-2=1` / `V-3=E` / `V-4=680`) · "
                  "`--selftest` rc=0 (11/11) · 5 个受保护 md5 逐字节不变 ⇒ ★**但这 11 条自测里没有一条查「行号有没有漂」**★ ⇒ "
                  "★**老板拍 A1/A2/A3 后一次落 14 条时, V-3 会删 3 行 DEMO_DNP ⇒ 网表/脚表所有行号锚点整体 -3 ⇒ 假绿**★ ⇒ "
                  "★**下一个按行号改东西的人 (人或 agent) 会改错行, 而门禁不会喊**★"),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": "False",
        "need_keys": "['iss230_row_shift_false_green']",
        "fix_ref": "None",
        "note": ("★**main 2026-11-17 00:4x 开单 (job 775d9893「ARS45 继续执行后继计划」)**: ★**本轮 advance.py 的 A 段 (internal) 起手为空** "
                 "(三个总工名下当时各卡一条 status=fixing 的僵尸单 ⇒ main 先把 ISS-258/259/260 三条独立复验签 verified 放行) ⇒ "
                 "★**main 自己开这三条主线内的单补位** ⇒ ★**本单 = 原理图主线正中央的一步 (老板 11-11 10:07: 先解决原理图绘制的问题, 再解决 PCB 绘制的问题)★** "
                 "⇒ ★**零落表 (V-2/V-3/V-4 老板都还没拍) · 零外发 · 不碰板/布线/布局 · 不替老板拍板** ★"),
    },
    {
        "id": "ISS-263",
        "title": ("★★[主线内·软件/工具链侧·demo 头号卡点·内部活] ★★★★[ISS-155 blocker 的 E-11/E-12] ★**官方独立工具链 `rknn3-toolkit 1.2.0` 本机安装实测 + "
                  "`config(target_platform='rk3572')` 实跑 + 一次完整模型转换** ★★ ⇒ ★**把「RK3572 的 .rknn 到底能不能转出来」从 [0数据] 变成有实测数** ★"),
        "severity": "blocker",
        "source_blocker": "ISS-155",
        "source_agent": "main",
        "desc": ("★ISS-250 (sw-lead, verified) 已查清: rknn-toolkit2 2.3.2 不认 rk3572 target, 但官方另发 **rknn3-toolkit 1.2.0** 支持 RK3572 (Beta) ⇒ "
                  "★**剩下的就是「本机装上 + 真跑一次」这一步没做**★ ⇒ ★**已知硬数字 (ISS-250 实测)**: wheel 102,657,410 B · "
                  "官方 md5 `a972e03af94fd18e21f026558735b28d` · 依赖 numpy>=2.0 / torch>=2.2 ⇒ 必须独立 conda env (python3.10) · "
                  "下载速率单路 ≈6.2 KB/s / 7 路并发 ≈43.5 KB/s ⇒ 单路 ≈4.6 h / 并发 ≈0.47 h ⇒ "
                  "★**板不可达 ⇒ 板端接受性仍是 [0数据], 这一层不许含糊**★"),
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": "False",
        "need_keys": "['iss250_e11_e12_pending_install_test']",
        "fix_ref": "None",
        "note": ("★**main 2026-11-17 00:4x 开单 (job 775d9893)**: ★**ISS-250 的 E-11/E-12 待办一直挂在 needs_from 里没人接** ★ "
                 "⇒ ★**本单 = demo 头号卡点 (ISS-155 blocker) 的最后一跳** ★ ⇒ "
                 "★**零外发邮件 · 零采购 (老板 11-04 明令不许再提买板) · 不污染 toolkit2 2.3.2 环境 · 路线取舍仍由老板拍** ★"),
    },
    {
        "id": "ISS-264",
        "title": ("★★[主线内·结构侧·口径收口·内部活] ★★`MECH/service_port_check.py` 三处常量还停在旧 15mm 板口径 (`p2_y 7.50` / `s2_y 12.50` · 脚本自己的注释就写着「Y 已作废」) ★★ "
                  "⇒ ★**迁到现行 demo 板 60×30 套A 口径 (P2 52.00/15.00 · S2 52.00/20.00) + 受保护脚本 H-1 重基线 + 补登 ISS-253 分片** ★"),
        "severity": "medium",
        "source_blocker": "ISS-085",
        "source_agent": "main",
        "desc": ("★main 2026-11-17 00:3x grep 实测 `MECH/service_port_check.py`: L41 `pcb_thk 1.00` (已是现行口径, 只核不动) · "
                  "L106 `p2_y 7.50` · L107 `s2_y 12.50` ⇒ ★**两个 Y 仍是旧 15mm 板口径** ★ ⇒ "
                  "★**迁完后 §5.1 开口 Y 与 P-5 最近距离 (文档记 3.23mm / 8.53mm) 都要重算** ★ ⇒ "
                  "★**依据 = 板宽 30mm (老板 10-29 19:16 放宽, ISS-118) + 孔位套A (ISS-194 verified) + MECH/BOARD_GEOM_30MM.md** ⇒ "
                  "★**这是口径收口, 不是新决策 ⇒ main 授权改受保护脚本 + 走 H-1 重基线** ★ "
                  "★**附带**: ISS-259 交卷报告发现 #1 = mech-lead 上一跳 ISS-253 的分片条目没落盘 (`grep -c iss253 state/fragments/mech.yaml` = 0) ★"),
        "owner": "mech-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": "False",
        "need_keys": "['iss251_mech_service_port_pad_y_migrate']",
        "fix_ref": "None",
        "note": ("★**main 2026-11-17 00:4x 开单 (job 775d9893)**: ★**本单由 mech-lead 自己的 need `iss251_mech_service_port_pad_y_migrate` 转成内部单** ★ "
                 "⇒ ★**main 授权**: 板宽 30mm + 套A 是老板已拍口径 ⇒ 迁常量不构成新决策 ★ "
                 "⇒ ★**零落表 · 零外发 · 不碰 PCB 布线/布局 (那 6 个 PCB 类 FAIL 是正确状态, 排队) · 不替老板拍板** ★"),
    },
]

BRIEF_FILES = {
    "ISS-262": "state/dispatch_briefs/ISS-262_hw_land_row_anchor_guard.md",
    "ISS-263": "state/dispatch_briefs/ISS-263_sw_rknn3_toolkit_install_test.md",
    "ISS-264": "state/dispatch_briefs/ISS-264_mech_service_port_const_migrate.md",
}


def dump_block(d: dict) -> str:
    txt = yaml.safe_dump(d, allow_unicode=True, default_flow_style=False, sort_keys=False, width=1000000)
    lines = txt.rstrip("\n").split("\n")
    out = ["- " + lines[0]]
    for ln in lines[1:]:
        out.append("  " + ln)
    return "\n".join(out) + "\n"


def block_bounds(lines, iid):
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("- id: "):
            if start is not None:
                return start, i
            if ln[len("- id: "):].strip() == iid:
                start = i
    if start is None:
        return None, None
    return start, len(lines)


def main() -> int:
    shutil.copy2(LOG, BAK)
    lines = open(LOG, encoding="utf-8").read().split("\n")

    # ---------- 1) 三条僵尸单签 verified ----------
    for iid, meta in VERIFY.items():
        s, e = block_bounds(lines, iid)
        if s is None:
            print("❌ 找不到 %s" % iid)
            return 2
        blk = lines[s:e]
        # 就地替换单行键
        for j, ln in enumerate(blk):
            if ln == "  status: fixing":
                blk[j] = "  status: verified"
            elif ln.startswith("  fix_ref:") and meta.get("fix_ref"):
                blk[j] = "  fix_ref: %s" % q(meta["fix_ref"])
            elif ln == "  verify_result: null":
                blk[j] = "  verify_result: pass"
            elif ln == "  verify_date: null":
                blk[j] = "  verify_date: %s" % q(TODAY)
        # 块尾追加缺的 verify 键 + verify_note
        keys = {ln.split(":", 1)[0].strip() for ln in blk if ln.startswith("  ") and ":" in ln and not ln.startswith("    ")}
        add = []
        if "verify_by" not in keys:
            add.append("  verify_by: main")
        if "verify_result" not in keys:
            add.append("  verify_result: pass")
        if "verify_date" not in keys:
            add.append("  verify_date: %s" % q(TODAY))
        add.append("  verify_note: %s" % q(meta["verify_note"]))
        # 插到块尾 (去掉块尾多余空行)
        while blk and blk[-1].strip() == "":
            blk.pop()
        blk.extend(add)
        lines[s:e] = blk

    # ---------- 2) 追加三条新单 ----------
    out = []
    for d in NEW:
        d = dict(d)
        d["task_brief"] = open(os.path.join(PROJ, BRIEF_FILES[d["id"]]), encoding="utf-8").read()
        out.append(dump_block(d))

    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(out)
    open(LOG, "w", encoding="utf-8").write(text)

    # ---------- 3) 自检 ----------
    d2 = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d2["issues"]}
    print("issues total:", len(ids))
    for iid in VERIFY:
        it = ids[iid]
        print("  %s -> %s (verify_by=%s verify_result=%s verify_date=%s)" % (
            iid, it["status"], it.get("verify_by"), it.get("verify_result"), it.get("verify_date")))
    for d in NEW:
        it = ids[d["id"]]
        print("  %s -> %s owner=%s due=%s brief=%d B" % (
            d["id"], it["status"], it["owner"], it["due"], len(it.get("task_brief") or "")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
