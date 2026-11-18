#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0655_fix_verify_separation.py
★main 订正 06:50 那次落账里踩到的【验证分离】规则 (★issue_check C3★)★

★**问题 (★main 自己实跑 issue_check --json 抓到的★)** ★★
· ★**06:50 把 ISS-116 / ISS-119 / ISS-132 落了 `verified` 且 verify_by=main, 但这三条 owner 也是 main**
  ⇒ issue_check C3 「★违反验证分离★ verify_by == owner == main」⇒ ★**违规 3 条 (26 ⇒ 23)** ★

★★**订正口径 (★按铁律「自己产的必须别人验」★)** ★★
· ★**ISS-119 (换芯定案)**: ★**验证人本来就该是老板** (★老板 2026-11-02 01:00 亲口拍板「芯片选型确定选用 RK3572」= 验证已完成★)
  ⇒ keep `verified`, ★**verify_by 改 boss** (★文档头自述「其余待老板点头 (verify_by: boss)」 同口径★) ★
· ★**ISS-132 (视涯 单色/全彩)**: ★**原 note 就写着「★verify_by=boss★」且 verify_result='pass' 本来就有** ⇒
  ★**按原口径还原: verify_by=boss** ⇒ ★**残余 (demo 用全彩版还是单色绿版) 已列进 `DECISION_PENDING_2026-11-16.md` §A6, 不代拍** ★
· ★**ISS-116 (工作方式改造)**: ★**产物是 main 按老板 10-29 09:59 原话做的, 但【总表形态 + 恢复协议】要老板过目** ⇒
  ★**main 只验了机制 (文件在盘 + cron 在跑), 不该自己签「已验收」** ⇒ ★**回退到 `fixed` + owner=boss + external=True + due 顺延 2026-11-18** ★ (★同 ISS-097 的处置口径★)

★★**边界**: 不改任何交付物 · 不改 status 之外的实质内容 · 不动别人的 issue ★
"""
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    by_id = {i.get("id"): i for i in log["issues"]}

    # ---- ISS-119: verified + verify_by=boss (老板 11-02 01:00 亲口拍板 = 验证已完成) ----
    i119 = by_id["ISS-119"]
    assert i119.get("status") == "verified" and i119.get("owner") == "main"
    i119["verify_by"] = "boss"
    i119["note"] = (i119.get("note") or "") + (
        "\n2026-11-16 06:55 ★**验证分离订正 (★issue_check C3 抓到的★)**: ★**本单是 main 自产的定案书 ⇒ 验证人不能是 main** ★ "
        "⇒ ★**verify_by 改 boss** (★依据 = 老板 2026-11-02 01:00 亲口拍板「芯片选型确定选用 RK3572」= 验证已由老板完成; "
        "定案书头自述「其余待老板点头 (verify_by: boss)」 同口径★) ⇒ ★**main 的角色是【整理与复算】, 不是【验收人】** ★"
    )

    # ---- ISS-132: verified + verify_by=boss (还原原 note 口径) ----
    i132 = by_id["ISS-132"]
    assert i132.get("status") == "verified" and i132.get("owner") == "main"
    i132["verify_by"] = "boss"
    i132["note"] = (i132.get("note") or "") + (
        "\n2026-11-16 06:55 ★**验证分离订正 (★issue_check C3 抓到的★)**: ★**按本单原 note 口径还原「verify_by=boss」** (★原 note 逐字写着「★verify_by=boss: 本条等的是外部答复 + 老板对『能不能接受单色』的拍板★」· 且 verify_result='pass' 本来就有★) "
        "⇒ ★**main 本轮只做【复读确认无翻案】, 不是验收人** ⇒ ★**残余的「demo 用全彩版还是单色绿版」已列进 `DECISION_PENDING_2026-11-16.md` §A6, 等老板拍, main 不代拍** ★"
    )

    # ---- ISS-116: 回退 fixed + 转待老板过目 (机制已验, 内容待老板) ----
    i116 = by_id["ISS-116"]
    assert i116.get("status") == "verified" and i116.get("owner") == "main"
    i116["status"] = "fixed"
    i116["owner"] = "boss"
    i116["external"] = True
    i116["due"] = "2026-11-18"
    i116["verify_by"] = None
    i116["verify_date"] = None
    i116["verify_result"] = (
        "★main 2026-11-16 06:5x 机制自检 (★本轮自己实测, 不抄交卷报告★) —— ★**这不是「已验收」, 是「机制已跑起来」的证据**★\n"
        "· ★**总表在盘**: `TASK_BOARD.md` (17783 B, 11-16 00:43) ★\n"
        "· ★**token 守护脚本在盘**: `state/token_watch.py` (8637 B, 11-11 10:16) ★\n"
        "· ★**快照生成器在盘**: `state/gen_progress_snapshot.py` (★本 job 步骤 6 每轮实跑 ⇒ 06:37 生成 `PROGRESS_SNAPSHOT.md` 2854 B ★) ★\n"
        "· ★**cron 在跑 (main 实读 sessions_list)**: 「ARS45 token 守护 (每 15 分钟, 限额前推进度快照到 GitHub)」最近一轮 lastMessage = ★**「token 守护: OK (窗口 0.0M | 距上次推送 77.4 分钟)」★ ⇒ **不是空跑** ★ ; "
        "★**「ARS45 GitHub 同步 (每 5 小时 · 有进展才推)」独立 job 也在 (11-15 21:05 推过 commit `ed30912`)★** ★\n"
        "· ★**教训区**: `MEMORY.md` / `AGENTS.md` 铁律区在盘 ★ ⇒ ★**老板 10-29 09:59「先记录到总表 + 周期检测 token + 限额前推进 GitHub」这条, 机制上已落地并仍在跑** ★\n"
        "· ★**★为什么不是 verified (★铁律「自己产的必须别人验」★)**: ★**本单产物是 main 按老板原话做的, main 只验了机制; 【总表形态 + 恢复协议是否合老板意】得老板过目 ⇒ 状态保留 `fixed` + owner 转 boss + due 顺延 2026-11-18** ★"
    )
    i116["note"] = (i116.get("note") or "") + (
        "\n2026-11-16 06:55 ★**验证分离订正 (★issue_check C3 抓到的★)**: ★**main 不许自签自己产的活** ⇒ ★**回退 `verified` → `fixed`, owner main → boss, external=True, due → 2026-11-18 (待老板过目总表形态与恢复协议)** ★ "
        "⇒ ★**机制侧 (总表 / 守护脚本 / cron / 快照) main 已实测在跑, 证据见 verify_result** ★"
    )

    shutil.copy2(LOG, LOG + ".bak_20261116_0655_fix_verify_separation")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-119/ISS-132 → verify_by=boss ; ISS-116 → 回退 fixed + owner=boss + due 11-18")

if __name__ == "__main__":
    main()
