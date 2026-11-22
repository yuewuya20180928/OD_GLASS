#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1510_verify242_brieffix_redispatch244.py
★main (moli) 2026-11-16 15:1x (cron fb67af40 ARS45 队列自动派活)★

★★★**本脚本做三件事 (★全部本机实跑过, 不抄任何交卷报告★)** ★★★
★**① ISS-242 (hw-lead) 独立复验 ⇒ 落 verified (清 hw-lead 名额)** ★
   · ★**会话**: `agent:hw-lead:subagent:2fcfe9b5` (session 5b030d1c) 13:48:17 起 · 14:45:37 止 · runtime 1638s · ★**status=done** ★ ⇒ **真交卷**
   · ★**main 自己实跑**: `python3 HW/check_netlist_contradiction_r3.py` ⇒ **rc=1 且恰 3 条 findings** (零多报零少报) ·
     `--selftest` ⇒ **rc=0 · 11/11 全抓到** (每条自证「变异生效/变异前绿/变异后红」) ·
     `python3 HW/check_netlist_selfconsistency.py` ⇒ **rc=0** (★注意: 真路径在 `HW/` 下, 不在 `state/` 下★) ·
     `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (★【Q1】18/18★)
   · ★**5 个受保护 md5 逐字节未变**: 网表 34132f7e… · 脚表 b21b743a… · BOM c195a117… · 板 611b869e… · .kicad_pro 3e504d2b…
   · ★**三件交付物在盘**: `HW/NETLIST_CONTRADICTION_R3_CLOSEOUT.md` 32113 B · `HW/check_netlist_contradiction_r3.py` 39065 B ·
     `HANDOFF/2026-11-16_hw-lead_ISS242_网表板第3轮自相矛盾3条.md` 37754 B
   · ★**本单零落表** (网表/脚表/BOM 一字没改) ⇒ ★**ISS-243 动手前仍必须自己读盘** ★
★**② ISS-243 brief 修两处 (★派活前的"命令存在性"闸点名的★)**
   · ★**`HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md`** —— 这条是**本单交卷单产出物** (交卷时还不存在)
     ⇒ ★**按 check_brief_commands.py 自己的约定补上「★新建★」显式声明** ⇒ 闸才不把它误判成"坏命令" ★
   · ★**追加一条事实**: ISS-242 已于 14:45 交卷 + main 15:1x 复验落 verified ⇒ ★**本单的前置条件已满足, 可以开跑** ★
★**③ ISS-244 brief 改成【续做重派】版 (★上一轮会话 14:52 撞 timeout 死了, 盘上零产出★)**
   · ★**会话**: `agent:sw-lead:subagent:e1e972d2` (session c2315fc7) 14:43:10 起 · 14:52:04 止 · runtime 484s · ★**status=timeout / abortedLastRun=true** ★
   · ★**盘上零产出**: `HW/PART_SELECTION_GAPS_CLOSEOUT.md` 不存在 · `HW/check_part_selection_gaps*.py` 不存在 ·
     `HANDOFF/2026-11-16_sw-lead_ISS244_*.md` 不存在 ⇒ ★**4 件交付物一件没落 ⇒ 僵尸 fixing ⇒ 必须重派** ★
   · ★**上一轮干到哪 (★只在会话内存里, 盘上没有★)**: 已在抓 LED 厂商手册的 Iv-vs-If 曲线并做图像数字化
     (APH1608SURCK 红光: If=1.00mA→0.0487 · 1.10→0.0554 · 1.20→0.0588 · 1.30→0.0655 · 1.50→0.0722 · 2.00→0.0991 · 3.00→0.1495 · 5.00→0.2537 · 归一化到 20mA 档) ★
   · ★**同一个 HANDOFF 路径也要补「★新建★」声明** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml`** (ISS-242 的 status/verify_result/note + ISS-243/ISS-244 的 task_brief) ★
· ★**不改任何交付物文件** · ★**不碰 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** ★
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM** · ★**零外发** · ★**未替老板拍板** ★
· ★**不改 dispatch_log.yaml** (★派活时由 advance.py --apply 写★) ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
IL_LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"

# ---------------------------------------------------------------- ISS-242 复验
VERIFY_242 = (
    "★main (moli) 2026-11-16 15:1x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**会话**: `agent:hw-lead:subagent:2fcfe9b5` (session 5b030d1c) 13:48:17 起 · 14:45:37 止 · runtime 1638s · ★**status=done** ★ ⇒ **真交卷** ★\n"
    "· ★**main 自己实跑 4 道闸**: `python3 HW/check_netlist_contradiction_r3.py` ⇒ **rc=1 且恰 3 条 findings** (★主线那 3 条缺陷·零多报零少报★) · "
    "`--selftest` ⇒ **rc=0 · 11/11 全抓到** (★每条都自证「变异生效 / 变异前绿 / 变异后红」★) · "
    "`python3 HW/check_netlist_selfconsistency.py` ⇒ **rc=0** (★**真路径在 `HW/` 下, 不在 `state/` 下** ⇒ ISS-242 的任务书里写 `state/check_netlist_selfconsistency.py` 是**路径笔误**, 闸因递归兜底没抓到, 本次订正★) · "
    "`python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (★【Q1】18/18★)\n"
    "· ★**三件交付物 main 亲测在盘**: `HW/NETLIST_CONTRADICTION_R3_CLOSEOUT.md` 32113 B (mtime 14:44) · "
    "`HW/check_netlist_contradiction_r3.py` 39065 B (mtime 14:28) · "
    "`HANDOFF/2026-11-16_hw-lead_ISS242_网表板第3轮自相矛盾3条.md` 37754 B (mtime 14:45) ★\n"
    "· ★**5 个受保护 md5 逐字节未变**: 网表 34132f7e40a241e1fae1476be0eafbd5 · 脚表 b21b743a7702d30729f0d653c15392df · "
    "BOM c195a117ff17490d4d1e1a5b8f1995a7 · 板 611b869e13518c3c023fb178f91a0075 · .kicad_pro 3e504d2be83152e337949723e909be1b ★\n"
    "· ★**本单零落表** (★网表/脚表/BOM/板 一个字节没改 ⇒ 3 条缺陷**仍在盘上**, 只出了规格与门禁★) ⇒ ★**ISS-243 动手前仍必须自己读盘** ★\n"
    "· ★**未替老板拍板**: V-2 / V-3 / V-4 / G-1 一条没代拍 ⇒ F2 (J_CHG 位号消歧) 留给 main 排期 ★"
)

NOTE_242 = (
    "\n\n★2026-11-16 15:1x (cron fb67af40 队列自动派活) ★**main 独立复验 ⇒ 落 verified · 清 hw-lead 名额** ★\n"
    "· ★**依据 (★main 本轮自己实跑, 不采信 agent 自述★)**: 门禁 rc=1 恰 3 条 · --selftest rc=0 11/11 · selfconsistency rc=0 · merge rc=0 · gate_check rc=0 Q1 18/18 · "
    "★**5 个受保护 md5 逐字节未变** · 三件交付物在盘 ★\n"
    "· ★**为什么必须清 (★不是形式主义★)**: status=fixing ⇒ advance.py 的 in_flight 判据挡住 hw-lead ⇒ ★**hw-lead 唯一写会话名额被『已交卷但没签字』占着** ⇒ A 段开不出来 ★\n"
    "· ★**清账后 hw-lead 名额释放** ⇒ ★**本轮已派 ISS-243 (hw-lead)** ★\n"
    "· ★**边界**: 只改本条 status/verify_result/verify_by/verify_date/note · 零外发 · 零落表 · 零 PCB 触碰 · 没碰任何分片 / 真源文件 / outbox ★"
)

# ---------------------------------------------------------------- ISS-243 brief 补丁
# ① HANDOFF 路径是本单产出 ⇒ 按闸的约定补「★新建★」显式声明
OLD_243_HANDOFF = "· ★**交卷单** `HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md`"
NEW_243_HANDOFF = "· ★**交卷单 (★新建★)** `HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md`"

# ② 前置条件已满足 (ISS-242 已交卷并落 verified) ⇒ 追加一条事实, 不改原文
APPEND_243 = (
    "\n★★**★注 (★main 2026-11-16 15:1x 追加·★不改上面任何原文★)★★** ★\n"
    "★**① ISS-242 已于 14:45 交卷, main 15:1x 独立复验落 verified** (★门禁 rc=1 恰 3 条 · --selftest 11/11 · merge+gate_check rc=0 Q1 18/18 · 5 受保护 md5 逐字节未变★) "
    "⇒ ★**上面那句「ISS-242 交卷签字前不许开跑」的前置条件已满足 ⇒ 本单可以开跑** ★\n"
    "★**② 但 ISS-242 只出规格、零落表** ⇒ ★**网表里 `C_VBUS_OUT`/`C_VBUS_GND` 那两颗 2 脚电容各落进 3 个网的缺陷仍在盘上** ⇒ "
    "★**你本单只许改 `C_REGN` 那几行 (L1), 不许顺手修它** ⇒ 修它归落表批次 (★main 排期★) ★\n"
    "★**③ 交卷单路径 `HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md` 是本单产出物 (★交卷时还不存在★) ⇒ 已在上面标注「★新建★」, "
    "★不是让你去读一个已存在的文件** ★\n"
    "★**④ 派活预算**: runTimeout 5400s ⇒ ★**建议顺序: 先 L1 落表 (3 处改 + 备份 + 台账登记 + 4 道闸) ⇒ 再 L2 映射表 ⇒ 再 L3 改法 ⇒ 再 L4 清单 ⇒ 最后写门禁 + --selftest + 交卷单 + 分片** ★\n"
)

# ---------------------------------------------------------------- ISS-244 续做重派补丁
OLD_244_HANDOFF = "★**交卷单** `HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md`"
NEW_244_HANDOFF = "★**交卷单 (★新建★)** `HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md`"

REDISPATCH_244 = (
    "★**续做派活 (★main 2026-11-16 15:1x 实测: 上一轮会话 14:43:10~14:52:04 撞 timeout (runtime 484s · abortedLastRun=true · status=timeout) "
    "⇒ ISS-244 是【零产出僵尸】★) ⇒ ★**本轮重派 · runTimeout 5400s** ★**\n"
    "★★**上一轮到底干到哪 (★main 读会话 transcript 实测, 不是猜★)** ★★\n"
    "· ★**会话**: `agent:sw-lead:subagent:e1e972d2` (session c2315fc7) · 88 条记录 · ★**死在 G-5 (LED 亮度) 的厂商 Iv-vs-If 曲线图像数字化上** ★\n"
    "· ★**盘上零产出** (★main 实测 ls★): `HW/PART_SELECTION_GAPS_CLOSEOUT.md` **不存在** · `HW/check_part_selection_gaps*.py` **不存在** · "
    "`HANDOFF/2026-11-16_sw-lead_ISS244_*.md` **不存在** ⇒ ★**4 件交付物一件没落 ⇒ 交卷 = 0** ★\n"
    "· ★**上一轮已抓到但没落盘的数 (★只在会话内存里★)**: ★**APH1608SURCK (Hyper Red AlGaInP 0603) 的 Iv-vs-If 曲线数字化归一化值** ⇒ "
    "If=1.00mA→0.0487 · 1.10→0.0554 · 1.20→0.0588 · 1.30→0.0655 · 1.50→0.0722 · 2.00→0.0991 · 3.00→0.1495 · 5.00→0.2537 "
    "(★线性自洽: 3.00mA→0.1495 ≈ 0.15 · 2.00mA→0.0991 ≈ 0.10 ⇒ 说明数字化本身是准的★) ⇒ ★**本轮要把它变成盘上的证据 (出处 + 图号/页码 + 数字化方法), 别只写一句「查到了」** ★\n"
    "★★**本轮怎么干 (★main 给的顺序建议, 不是重写任务书★)** ★★\n"
    "· ★**① 先落盘再研究** ⇒ ★**第一件事 = 把 4 件交付物的骨架先建起来** (收口页 + 门禁脚本 + 交卷单 + 分片) ⇒ ★**再往里填** ⇒ "
    "★**这样就算再撞 timeout, 盘上也有半成品, 下一轮不用从零开始 (★这正是上一轮的教训: 9 分钟全花在内存里, 盘上零产出★)** ★\n"
    "· ★**② G-5 的 PDF 请落到盘上** (★例: 存 `HW/PART_SELECTION_GAPS_CLOSEOUT.md` 同目录或 `state/.cache_iss244/`★) ⇒ ★**数字化脚本也落盘** ⇒ ★**出处可复核** ★\n"
    "· ★**③ 四条重点缺口 (G-5 / G-3+G-4 / G-10 / G-1) 优先于 22 件 OPN 清单** ⇒ ★**时间不够就把 OPN 清单先写「锚点 + 状态」骨架, 研究缺口优先** ★\n"
    "· ★**④ 抓取纪律照旧**: `web_search` / `web_fetch` + ★**带 `--max-time` 的 curl** (★本机上一轮 curl 卡死过★) + `pdftotext` 实读 ★\n"
    "· ★**⑤ 门禁与 --selftest 别放到最后才写** ⇒ ★**先写门禁 (6 条断言) 再补正文**, 这样边补边能跑 rc ★\n"
    "★**其余边界一个字没变**: 零外发 · 不改网表/脚表/BOM · 不改板/布线/布局 · 不改 ISS-241 矩阵正文 · 不替老板拍板 · 不改 issue_log · 实物 [实测] = 0 条 ★\n"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(IL, IL + ".bak_20261116_1510_verify242_brieffix_redispatch244")

    lf = open(IL_LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        issues = il.get("issues") or []
        by_id = {it.get("id"): it for it in issues}

        # --- ① ISS-242 落 verified
        it242 = by_id.get("ISS-242")
        if not it242:
            raise SystemExit("★ISS-242 不存在 ⇒ 中止")
        if it242.get("status") != "fixing":
            raise SystemExit("★ISS-242 status=%s (不是 fixing) ⇒ 中止" % it242.get("status"))
        it242["status"] = "verified"
        it242["verify_by"] = "main"
        it242["verify_date"] = TODAY
        it242["verify_result"] = VERIFY_242
        it242["fix_ref"] = (
            "HW/NETLIST_CONTRADICTION_R3_CLOSEOUT.md (3 条逐条定性 + 逐字改法) · "
            "HW/check_netlist_contradiction_r3.py (5 条断言 + --selftest 11/11) · "
            "HANDOFF/2026-11-16_hw-lead_ISS242_网表板第3轮自相矛盾3条.md (B1~B6)"
        )
        it242["note"] = (it242.get("note") or "") + NOTE_242

        # --- ② ISS-243 brief: 补「★新建★」+ 追加前置条件已满足的事实
        it243 = by_id.get("ISS-243")
        if not it243:
            raise SystemExit("★ISS-243 不存在 ⇒ 中止")
        b243 = it243.get("task_brief") or ""
        if OLD_243_HANDOFF not in b243:
            raise SystemExit("★ISS-243 brief 里找不到交卷单那一行 ⇒ 中止 (brief 已被改过)")
        b243 = b243.replace(OLD_243_HANDOFF, NEW_243_HANDOFF, 1)
        b243 = b243.rstrip() + "\n" + APPEND_243
        it243["task_brief"] = b243

        # --- ③ ISS-244 brief: 续做重派抬头 + 补「★新建★」
        it244 = by_id.get("ISS-244")
        if not it244:
            raise SystemExit("★ISS-244 不存在 ⇒ 中止")
        b244 = it244.get("task_brief") or ""
        if OLD_244_HANDOFF not in b244:
            raise SystemExit("★ISS-244 brief 里找不到交卷单那一行 ⇒ 中止 (brief 已被改过)")
        b244 = b244.replace(OLD_244_HANDOFF, NEW_244_HANDOFF, 1)
        b244 = REDISPATCH_244 + b244
        it244["task_brief"] = b244
        it244["note"] = (it244.get("note") or "") + (
            "\n\n★2026-11-16 15:1x (cron fb67af40 队列自动派活) ★**上一轮会话 14:43:10~14:52:04 撞 timeout (runtime 484s · abortedLastRun=true) ⇒ "
            "盘上零产出 (收口页/门禁/交卷单/分片 四件一件没落) ⇒ 僵尸 fixing ⇒ 本轮改成【续做重派】brief 并重派** ★"
            "\n· ★**上一轮死在哪**: G-5 (LED 亮度) 的厂商 Iv-vs-If 曲线图像数字化 (APH1608SURCK 归一化值已在会话内存里, 盘上零产出) ★"
            "\n· ★**本轮要求**: 先落盘骨架再填内容 (★上一轮的教训: 9 分钟全在内存里★) · PDF 与数字化脚本要落盘 · 四条重点缺口优先于 22 件清单 ★"
        )

        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()

    print("   - ISS-242 → verified (main 亲核签字: 门禁 rc=1 恰3条 + selftest 11/11 + selfconsistency rc=0 + merge/gate rc=0 Q1 18/18 + 5 md5 未变)")
    print("   - ISS-243 brief 修: 交卷单路径补「★新建★」声明 + 追加「ISS-242 已 verified ⇒ 可开跑」")
    print("   - ISS-244 brief 改: 【续做重派】抬头 (零产出僵尸) + 交卷单路径补「★新建★」声明")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
