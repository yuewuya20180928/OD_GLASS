#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 03:3x · job 775d9893「ARS45 继续执行后继计划」
★(1) 开一条主线内的新单 (ISS-268 · owner=hw-lead · 作业包 v3 §0 两行口径订正)★
★**只动 state/issue_log.yaml 一个文件 (末尾追加一块) · 不碰真源 / 分片 / 决策页 / PROJECT_TRACKER§0 / 板 / 网表★**
★**纪律: 原文件里 note / task_brief / desc 是多行标量 ⇒ 本脚本【绝不改写它们】(改写会打断 YAML 续行)★**
★只做: 文件尾追加新块 + 自检 (id 存在 / 字段齐 / brief 长度)★**
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0335_main_open_iss268"
BRIEF = "state/dispatch_briefs/ISS-268_hw_workpacket_caliber_fix.md"

TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


def dump_block(d: dict) -> str:
    txt = yaml.safe_dump(d, allow_unicode=True, default_flow_style=False, sort_keys=False, width=1000000)
    lines = txt.rstrip("\n").split("\n")
    out = ["- " + lines[0]]
    for ln in lines[1:]:
        out.append("  " + ln)
    return "\n".join(out) + "\n"


NEW = [
    {
        "id": "ISS-268",
        "title": ("★★[主线内·PCB 侧·口径订正·内部活] ★★「板只改一次」作业包 v3 (`HW/PCB/BOARD_ONEPASS_WORKPACKET.md`) §0 那张「一句话结论」表有 ★**两行口径漂移**★: "
                  "① ★**「卡在老板的」那一行的 A1/A2/A3 三个拍板码与全项目权威映射【写反了】**(★权威 = A1=V-3 BAT_DET · A2=V-4 R_ILIM · A3=V-2 USB ESD★) ★ "
                  "② ★**「不用任何人就能走的」那一行把 S4 (★卡 W-1/W-2 的步★) 算成自由步, 且漏了 S6/S7/S13**★ ⇒ ★**而老板此刻正站在「回一句 A1/A2/A3 就能解锁落表」的门口** ★★"),
        "severity": "high",
        "source_blocker": "ISS-266",
        "source_agent": "main",
        "desc": ("★main 2026-11-17 03:2x 本机实跑 (★逐行读盘, 不抄交卷报告★):\n"
                 "★**① `BOARD_ONEPASS_WORKPACKET.md:16` (★§0「卡在老板的」行★) 写「A1 (V-2 USB ESD 方案) · A2 (V-3 BAT_DET 阻值) · A3 (V-4 R_ILIM 档位)」⇒ 【轮转了一位】★**\n"
                 "  · ★**权威真源四处逐字一致**: `state/land_v_values.py:2000` → `A_ITEM = {\"A1\": \"V-3\", \"A2\": \"V-4\", \"A3\": \"V-2\"}` (★落表器自己的映射★) · "
                 "`state/issue_log.yaml:11601` → 「拍板码映射: A1 = V-3 · A2 = V-4 · A3 = V-2 (与决策页 §A 逐字对应)」 · "
                 "`DECISION_PENDING_2026-11-16.md` §A-补7 → 「V-3 = A1 · V-4 = A2 · V-2 走法 = A3」 · "
                 "`HANDOFF/2026-11-17_hw-lead_ISS265_PCB布线死因根因与布局修正规格.md` (BAT_DET 行) → 「老板 A1 (V-3 BAT_DET)」★\n"
                 "  · ★**同一文件另两处跟着错**: `:132` (S5 卡点) 与 `:285` (§6 卡点表) 写「老板 (A2 / V-3)」⇒ V-3 的拍板码是 A1 ★\n"
                 "  · ★**★落表器是 fail-closed ⇒ 不会静默落错 (★安全事实, 必须写进交卷单★)★**: 三个白名单互不相交 (V-3 ∈ {E,A,D,DEG4} · V-4 ∈ {680,470,390} · V-2 ∈ {1,2}; `state/land_v_values.py:12` + `:1095`) ⇒ "
                 "★**错位标签的取值一律被挡下 ⇒ rc=2 + 零写盘** ⇒ ★**代价 = 老板白回一次, 不是落错值** ★\n"
                 "★**② `BOARD_ONEPASS_WORKPACKET.md:15` (§0「不用任何人就能走的」行) 写「S1 / S2 / S3 / S4 / S9 / S10 / S11 / S12」**\n"
                 "  · ★**同文件 `:123` (S4 自己的卡点行) 写「S4 是本单第一个真正卡在老板的步 (W-1/W-2)」⇒ ★**§0 与 §3 自相矛盾**★**\n"
                 "  · ★**`HANDOFF/2026-11-17_hw-lead_ISS266_板只改一次作业包v3.md:235` 写「不等任何人就能走的 10 步: S1/S2/S3/S6/S7/S9/S10/S11/S12/S13 ⇒ 只剩 S4 (W-1/W-2) 与 S8 (P7/A1/W-4/mech) 要老板拍」⇒ ★**交卷单与作业包 §0 不一致 (漏 S6/S7/S13, 多 S4)**★**\n"
                 "  · ★**排期后果 (★真风险, 不是字面错字★)**: S4 = B-3/B-4/B-5 = USB ESD 三件 (换封装 + 挪位 + 重画 land) ⇒ ★**若按 §0 当自由步先做, 随后 W-1/W-2 拍下来又要改封装 ⇒ 板 md5 变第二次 ⇒ 直接违反「板只改一次」铁律** ★"),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": "False",
        "need_keys": "[]",
        "fix_ref": "None",
        "note": ("★**main 2026-11-17 03:3x 开单 (job 775d9893「继续执行后继计划」)**: ★**本单 = ISS-266 作业包 v3 交卷后 main 逐行复核发现的 2 处口径漂移** ★ "
                 "⇒ ★**为什么现在开 (★时间窗就在今天★)**: 老板此刻正站在「回一句 A1/A2/A3 就解锁落表」的门口 ⇒ ★**他若照 §0 理解这三个字母, 所指全部错位** ★ "
                 "⇒ ★**只改文档两行 + 加一行权威指针 ⇒ 成本 15 分钟; 不改的代价 = 老板白回一次 + 落表器白拒一次 + 板那一趟可能按错口径排期** ★ "
                 "★**类别**: ★**内部活 · 文档口径订正类** (★零写板 · 零落表 · 零改判据★) ⇒ ★**不是老板级拍板** ★ "
                 "★**边界**: 零写板 · 零落表 · 只许改 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 一个文件 · 零外发 · 不代拍 A1/A2/A3 取值 / W-1/W-2/W-4 / P7 / jd_y0 ★ "
                 "★**注意**: hw-lead 名下此刻有 ISS-262 (fixing) 在飞 ⇒ 本单等名额空出再派 (★不要与在飞单并发写同一文件★) ★"),
    },
]


def main() -> int:
    shutil.copy2(LOG, BAK)
    text = open(LOG, encoding="utf-8").read()
    if not text.endswith("\n"):
        text += "\n"

    out = []
    for d in NEW:
        d = dict(d)
        d["task_brief"] = open(os.path.join(PROJ, BRIEF), encoding="utf-8").read()
        out.append(dump_block(d))

    with open(LOG, "w", encoding="utf-8") as f:
        f.write(text + "\n".join(out))

    # ---------- 自检 ----------
    d2 = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d2["issues"]}
    print("issues total:", len(ids))
    for d in NEW:
        it = ids.get(d["id"])
        if not it:
            print("  ❌ %s 没落进去" % d["id"])
            return 2
        print("  %s -> %s owner=%s severity=%s due=%s brief=%d B need_keys=%s" % (
            d["id"], it["status"], it["owner"], it["severity"], it["due"],
            len(it.get("task_brief") or ""), it.get("need_keys")))
    # 旧单不许被动过 (条数 + 关键字段)
    print("  ISS-267 仍在:", ids.get("ISS-267", {}).get("status"))
    print("  ISS-266 仍在:", ids.get("ISS-266", {}).get("status"))
    print("  ISS-262/263/264:", ids.get("ISS-262", {}).get("status"),
          ids.get("ISS-263", {}).get("status"), ids.get("ISS-264", {}).get("status"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
