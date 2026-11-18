#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 09:0x · job 775d9893「ARS45 继续执行后继计划」
★新开 ISS-281 (hw-lead) = 「板只改一次」的【S10 投产包 md5 清单落地】★
★**依据 = 本轮 main 独立复验 ISS-280 时挖到、ISS-280 自己登记但没开单的残留缺口, main 本机实读确认★**
★**只动 1 个文件: state/issue_log.yaml**★
★**不碰真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何既有门禁脚本**★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0900_open_iss281"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-281_hw_s10_manifest_spec.md")
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


TITLE = ("★★[★主线·PCB 线·纯规格+作业包追加式订正+机器闸类] ★★「板只改一次」的【S10 投产包 md5 清单落地】★★ "
         "⇒ ★**作业包 §3-S10 的量化判据写着「板统计里的 md5 == S6 重出后的板 md5」, 但盘上 `HW/PCB/production/doc/board-stats.txt` "
         "是 KiCad 统计报告导出 (1435 B), `grep -ci md5` = 0 ⇒ 那个字段【根本不存在】⇒ S10 无判可依** ★ "
         "⇒ ★**⇒ S10 是「板改完最后一次」的留证/投产步, 而投产包(73 文件) 与板之间目前【没有任何内容级绑定】** ★ "
         "⇒ ★**chain_gate 只判 mtime(产物不比板旧) ⇒ 板改一次, 旧 Gerber 只要 mtime 刷新就能冒充新货** ★ "
         "⇒ ★**⇒ ISS-280 的 D6「留证绑定」需要「产物绑定到哪一版板」, 而盘上没有任何文件能声明这件事** ★ "
         "⇒ ★**⇒ 本单 = 造一份【投产包清单文件】的格式契约 + 一道内容级机器闸 (零写板 · 零跑 gen_production_pack.sh)** ★")

DESC = """★main 2026-11-17 08:4x~09:0x 本机实读 + 实跑 (不抄交卷报告)★
★**① 作业包 §3-S10 的量化判据落不了地** ★: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L246 原文 = 「文件数 = 73 · Gerber = 32 · 板统计里的 md5 == S6 重出后的板 md5」; 而 `HW/PCB/production/doc/board-stats.txt` 首行 = `PCB statistics report` (KiCad 统计报告导出, 1435 B, mtime 2026-11-17 02:45:31), `grep -ci md5` = **0** ⇒ ★**盘上那个字段不存在 ⇒ 照字面验收 S10 无判可依** ★
★**② 为什么它卡在「板只改一次」的收口处** ★: `state/chain_gate.py` (S11) 是 mtime 口径 ⇒ 只判「产物旧不旧」, 判不了「产物是不是这一版板出的」; `HW/check_onepass_commit_order.py` (ISS-280) 的 D6 要「留证产物绑定到哪一版板」⇒ ★**而盘上没有任何一个文件能声明它绑定的是哪一版板 ⇒ S10 落完之后, 投产包与板之间是空的** ★
★**③ 为什么现在能派 (时机对)** ★: 本轮 main 已把 ISS-279 (SW 侧腿) 与 ISS-280 (提交时序守卫) 独立复验落 verified ⇒ ★**hw-lead 名下本轮无 in-flight 任务 ⇒ 真空** ★; 而 S10 是 B 类终段步, 现在只出【规格 + 闸】不跑 S10 ⇒ ★**零写板** ★
★**④ 与 ISS-280 的分界** ★: ISS-280 已 verified, 它的交付物 (`BOARD_ONEPASS_COMMIT_ORDER.md` / `BOARD_ONEPASS_MD5_LEDGER.md` / `check_onepass_commit_order.py`) ★**一个字不许动** ★; 本单只【追加】作业包 §3-S10 下面一节, 并新建自己的规格页 + 闸 ★
★**⑤ 一条硬边界 (★main 写进任务书★)** ★: ★**禁止跑 `state/gen_production_pack.sh`** ★ (★它是 `rm -rf "$OUT"` 后重建 ⇒ 跑一次 = 73 个文件全换 + mtime 全刷 ⇒ 污染 chain_gate 的「产物不比源旧」判定, 不可逆★) ⇒ ★**只许在沙盒副本里试; 真盘 `HW/PCB/production/**` 一个字节不许动** ★"""

NOTE = ("2026-11-17 09:0x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮 08:4x~08:5x 独立复验 ISS-280 时, "
        "从它交卷单里挖到一条它自己登记但没开单的残留缺口, main 本机实读确认后开成本单** ★\n"
        "⇒ ★**任务书 `state/dispatch_briefs/ISS-281_hw_s10_manifest_spec.md`** ★\n"
        "★**hw-lead 名下本轮无 in-flight 任务 (ISS-280 已于 08:5x 落 verified ⇒ 真空) ⇒ 本单是本轮给 hw-lead 的活** ★\n"
        "★**类别**: 内部活 · PCB 线 · 纯规格 + 作业包追加式订正 + 机器闸类 ⇒ ★**零写板 · 零落表 · 零跑投产包 · 零改既有判据阈值** ★\n"
        "★**本单是「板只改一次」那条铁律的【最后一环】**: 前置三单已齐 (ISS-277 HW 侧 / ISS-278 MECH 侧在飞 / ISS-279 SW 侧) + "
        "时序守卫已 verified (ISS-280) ⇒ ★**但 S10 落完之后, 投产包与板之间仍没有内容级绑定 ⇒ 本单补的就是这一环** ★\n"
        "★**不涉及任何拍板项 ⇒ 不用问老板, hw-lead 自己做完交卷, main 独立复验后落 verified** ★")

FIELDS = [
    ("id", "ISS-281"),
    ("title", TITLE),
    ("severity", "high"),
    ("source_blocker", None),
    ("source_agent", "main"),
    ("desc", DESC),
    ("owner", "hw-lead"),
    ("reporter", "main"),
    ("raised", TODAY),
    ("due", "2026-11-20"),
    ("status", "open"),
    ("external", False),
    ("need_keys", []),
    ("fix_ref", None),
    ("verify_by", None),
    ("verify_result", None),
    ("verify_date", None),
    ("note", NOTE),
    ("dispatched_at", TODAY),
]


def main() -> int:
    brief = open(BRIEF, encoding="utf-8").read()

    shutil.copy2(LOG, BAK)
    lines = open(LOG, encoding="utf-8").read().split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()

    block = []
    for k, v in FIELDS:
        if k == "id":
            block.append("- id: ISS-281")
        elif v is None:
            block.append("  %s: null" % k)
        elif isinstance(v, bool):
            block.append("  %s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, list):
            block.append("  %s: []" % k)
        else:
            block.append("  %s: %s" % (k, q(v)))
    block.append("  task_brief: %s" % q(brief))

    lines.extend(block)
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    # ---------- 自检 ----------
    d = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d["issues"]}
    it = ids["ISS-281"]
    print("  问题单总数 = %d" % len(d["issues"]))
    print("  ISS-281 status=%s owner=%s severity=%s due=%s external=%s"
          % (it["status"], it["owner"], it["severity"], it["due"], it["external"]))
    print("  task_brief 字节 = %d (源文件 %d, 一致=%s)"
          % (len(it["task_brief"]), len(brief), it["task_brief"] == brief))
    print("  verify_by=%s verify_result=%s (★必须都不是 hw-lead★)" % (it["verify_by"], it["verify_result"]))
    print("  其它条目状态没变 =", sum(1 for i in d["issues"] if i["id"] != "ISS-281"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
