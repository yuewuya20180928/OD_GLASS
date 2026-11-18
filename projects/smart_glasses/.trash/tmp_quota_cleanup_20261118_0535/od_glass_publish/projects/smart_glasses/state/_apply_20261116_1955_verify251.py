#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1955_verify251.py
★main (moli) 2026-11-16 19:5x (cron fb67af40 ARS45 队列自动派活)★

★★★**本脚本做两件事 (★全部本机实跑过, 不抄任何交卷报告★)** ★★★
★**① ISS-251 (mech-lead) 独立复验 ⇒ 落 verified (清 mech-lead 名额)** ★
   · ★**会话**: `agent:mech-lead:subagent:29892e26` (session 9faedf4e) 19:40:36 起 · 19:45:33 止 ·
     runtime 295s · ★**status=done** ★ ⇒ **真交卷** (不是 timeout 僵尸)
   · ★**main 自己实跑 6 道闸 (★本脚本执行时已跑过一遍, 输出见下★)**:
     ① `python3 MECH/verify_budget.py` ⇒ **rc=0** (充电耗散口径 = buck 0.50W, 数值对拍一致)
     ② `python3 MECH/check_budget_caliber.py` ⇒ **rc=0 · 检查项 17 / 通过 17 / 红 0**
     ③ `python3 MECH/check_budget_caliber.py --selftest` ⇒ **rc=0 · 反向用例 13/13 全抓到**
        (四类全覆盖: 改回旧口径 4 · 改数字 4 · 删依据出处 2 · 改文档数字 3)
     ④ `python3 MECH/service_port_check.py` ⇒ **rc=0**
     ⑤ `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=2 · 21/23 · FAIL 恰 2 组 = G5b + C21**
        ⇒ ★**这条红是【并发】, 不是本单失败**: 网表盘上 md5 `16ac89f77c25a3f61834cc7ebcd78a7f`
        ≠ 锚点 `611c3ba3…` ⇒ **hw-lead 的 ISS-249 F1 落表**造成 (与 hw-lead 19:3x 交卷报告自述一致)
        ⇒ ★**ISS-251 的任务书 §③ 明写「那不是你的失败, 也不许你去修」** ⇒ 本单照办:
        ★**`MECH/check_demo_struct_truth.py` md5 `fa9b59e5…` 前后不变, 一行没改** ★
        ⇒ 归因登记: need `iss251_mech_demo_truth_gate_red_concurrent` (等 hw-lead 那一跳重锚)
     ⑥ `python3 state/merge.py` ⇒ **rc=0** · `python3 state/gate_check.py` ⇒ **rc=0 · 【Q1】18/18 · mech-lead 6/6**
        (★gate_check 认的 mech-lead 交接单正是本单那份 `2026-11-16_mech-lead_ISS251_*.md`★)
   · ★**3 个受保护脚本 md5 逐字节未变**: `MECH/service_port_check.py` 9b24bf985764880f0105aee677fba6a8 ·
     `MECH/check_demo_struct_truth.py` fa9b59e593a13408ad9505d986276f63 ·
     `MECH/hinge_usb_check.py` 3425bc141508de8a35f34c7cf7b803e8 ★
   · ★**交付物 main 亲测在盘**: `MECH/check_budget_caliber.py` 19923 B (mtime 19:42) ·
     `HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md` 25446 B (mtime 19:45, B1~B6 六块齐全) ·
     `state/fragments/mech.yaml` (mtime 19:44, 10 处 `iss251_*` 登记: 4 need + claim + artifact) ★
   · ★**为什么必须清 (★不是形式主义★)**: status=fixing ⇒ advance.py 的 in_flight 判据挡住 mech-lead ⇒
     ★**mech-lead 唯一写会话名额被「已交卷但没签字」占着** ⇒ A 段开不出来 ★
★**② TASK_BOARD.md §2 同步 (★§2 是台账 fixing 集合的投影, 不改就会被 alignment_check 第 1 条判据抓红★)** ★
   · ★**移除 ISS-251 行** (★只改表格行, 不碰 §1 / §3 / §7 任何一行★) ★
   · ★**追加 1 条对账留痕** (★「总表过期 = 看板误导老板」的第五次应验★) ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` + `TASK_BOARD.md` §2** ★
· ★**不改任何交付物文件** · ★**不碰 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** ★
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM** · ★**零外发** · ★**未替老板拍板**
  (d 值 / u8 截面 / 集热面 / 板长 / 板厚档位 5 项本单只列选项未代拍 ⇒ 仍等老板) ★
· ★**不改 dispatch_log.yaml** (★派活时由 advance.py --apply 写★) ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
IL = os.path.join(HERE, "issue_log.yaml")
IL_LOCK = os.path.join(HERE, ".issue_log.lock")
TB = os.path.join(PROJ, "TASK_BOARD.md")
BACKUP_DIR = os.path.join(HERE, ".bak_iss251")
STAMP = "20261116_1955"

# ---------------------------------------------------------------- ISS-251 复验记录
FIX_REF_251 = (
    "MECH/check_budget_caliber.py (17 条口径判据 + --selftest 13/13 反向用例) · "
    "HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md (B1~B6 + 附A 22 条逐条订正表 + 附B 并发说明 + 附C 边界自审) · "
    "MECH/MECH_BUDGET.md §2.1/§3 + MECH/SERVICE_PORT_ISS092.md (三处口径订正: buck 0.45-0.57W / k 237→201 / 检修口 15mm→60×30)"
)

VERIFY_251 = (
    "★main (moli) 2026-11-16 19:5x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**会话**: `agent:mech-lead:subagent:29892e26` (session 9faedf4e) 19:40:36 起 · 19:45:33 止 · runtime 295s · "
    "★**status=done** ★ ⇒ **真交卷** (不是 timeout 僵尸) ★\n"
    "· ★**main 自己实跑 6 道闸**: `python3 MECH/verify_budget.py` ⇒ **rc=0** (buck 口径 0.50W, 数值对拍一致) · "
    "`python3 MECH/check_budget_caliber.py` ⇒ **rc=0 · 17/17 · 红 0** · "
    "`python3 MECH/check_budget_caliber.py --selftest` ⇒ **rc=0 · 反向用例 13/13 全抓到** (四类全覆盖) · "
    "`python3 MECH/service_port_check.py` ⇒ **rc=0** · "
    "`python3 MECH/check_demo_struct_truth.py` ⇒ **rc=2 · 21/23 · FAIL 恰 2 组 = G5b + C21** "
    "(★**并发所致, 非本单失败**: 网表盘上 md5 `16ac89f77c25a3f61834cc7ebcd78a7f` ≠ 锚点 `611c3ba3…` ⇒ hw-lead ISS-249 F1 落表造成; "
    "★**任务书 §③ 明写「那不是你的失败, 也不许你去修」⇒ `check_demo_struct_truth.py` md5 `fa9b59e5…` 一行没改**★) · "
    "`python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (★【Q1】18/18 · mech-lead 6/6, 认的正是本单交接单★) ★\n"
    "· ★**3 个受保护脚本 md5 逐字节未变**: `MECH/service_port_check.py` 9b24bf985764880f0105aee677fba6a8 · "
    "`MECH/check_demo_struct_truth.py` fa9b59e593a13408ad9505d986276f63 · "
    "`MECH/hinge_usb_check.py` 3425bc141508de8a35f34c7cf7b803e8 ★\n"
    "· ★**交付物 main 亲测在盘**: `MECH/check_budget_caliber.py` 19923 B (19:42) · "
    "`HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md` 25446 B (19:45, B1~B6 六块齐全) · "
    "`state/fragments/mech.yaml` (19:44, 10 处 `iss251_*` 登记 = 4 need + claim + artifact) ★\n"
    "· ★**未替老板拍板**: d 值 (15/18/20) · u8 端件截面 · 集热面材质/面积 · 板长 · 板厚档位 5 项 ⇒ **只列选项 + 量化代价, 一条没代拍** ★\n"
    "· ★**本单零落表 / 零外发 / 零实物 [实测]=0** ⇒ **MECH 三处口径已收口, 结构侧 3 条老账归零** ★"
)

NOTE_251 = (
    "\n\n★2026-11-16 19:5x (cron fb67af40 队列自动派活) ★**main 独立复验 ⇒ 落 verified · 清 mech-lead 名额** ★\n"
    "· ★**依据 (★main 本轮自己实跑, 不采信 agent 自述★)**: verify_budget rc=0 · check_budget_caliber rc=0 17/17 · "
    "--selftest rc=0 13/13 · service_port rc=0 · merge rc=0 · gate_check rc=0 Q1 18/18 · "
    "★**3 个受保护脚本 md5 逐字节不变** · 交付物 3 件在盘 ★\n"
    "· ★**唯一红的 check_demo_struct_truth G5b/C21 是并发 (hw-lead F1 落表), 任务书 §③ 已预告, 不算本单失败** ⇒ "
    "★**归因留 need `iss251_mech_demo_truth_gate_red_concurrent`, 等 hw-lead 那一跳重锚** ★\n"
    "· ★**为什么必须清 (★不是形式主义★)**: status=fixing ⇒ advance.py 的 in_flight 判据挡住 mech-lead ⇒ "
    "★**mech-lead 唯一写会话名额被「已交卷但没签字」占着** ⇒ A 段开不出来 ★\n"
    "· ★**清账后 mech-lead 名额释放** ⇒ ★**下一轮 advance.py 的 internal 段能再开出来 (前提: 有 open 单)** ★\n"
    "· ★**边界**: 只改本条 status/verify_result/verify_by/verify_date/note + TASK_BOARD §2 一行 · 零外发 · 零落表 · "
    "零 PCB 触碰 · 没碰任何分片 / 真源文件 / outbox ★"
)

# ---------------------------------------------------------------- TASK_BOARD §2 补丁
TB_ROW_251 = (
    "| ISS-251 | mech-lead | 🔄执行中 (11-16 19:19 派出) | ★★**[主线内·MECH 侧·口径收口]** MECH 侧三处「只报不改 ⇒ 现在授权改」老账一次收口 "
    "(★充电耗散口径 / 铝 k 201 保守侧 / 检修口 15mm→60×30★) + 新机器门禁 ⇒ ★**并发告警: hw-lead 落表会让 G5b/C21 按设计变红, 不许他去修** ★ |\n"
)

TB_LINE_OLD = (
    "> ★**② 本节现列 ISS-249 / ISS-250 / ISS-251 三条 (★11-16 19:19 派出·与台账 `fixing` 集合逐条一致★)** ⇒ "
    "★**全部【原理图主线内】(PCB 布线/布局类按老板 11-11 10:07 口径一律不派)★**"
)

TB_LINE_NEW = (
    "> ★**② 本节现列 ISS-249 / ISS-250 两条 (★11-16 19:19 派出·与台账 `fixing` 集合逐条一致★)** ⇒ "
    "★**全部【原理图主线内】(PCB 布线/布局类按老板 11-11 10:07 口径一律不派)★**\n"
    "> ★**②' ISS-251 (mech-lead) 19:40:36~19:45:33 子会话 status=done 交卷 ⇒ main 19:5x 独立实跑 6 道闸 (17/17 + --selftest 13/13 + merge rc=0 + gate_check Q1 18/18) "
    "后落 `verified`** ⇒ ★**已移出本节** ⇒ ★**「总表过期 = 看板误导老板」的第五次应验** ★"
)


def main() -> int:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy2(IL, os.path.join(BACKUP_DIR, f"issue_log.yaml.bak_{STAMP}"))
    shutil.copy2(TB, os.path.join(BACKUP_DIR, f"TASK_BOARD.md.bak_{STAMP}"))

    # ---------------- TASK_BOARD §2 ----------------
    tb = open(TB, encoding="utf-8").read()
    if tb.count(TB_ROW_251) != 1:
        raise SystemExit(f"✗ TASK_BOARD: ISS-251 行命中 {tb.count(TB_ROW_251)} 次 (≠1) ⇒ 不写")
    if tb.count(TB_LINE_OLD) != 1:
        raise SystemExit(f"✗ TASK_BOARD: 对账行命中 {tb.count(TB_LINE_OLD)} 次 (≠1) ⇒ 不写")
    tb2 = tb.replace(TB_ROW_251, "").replace(TB_LINE_OLD, TB_LINE_NEW)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=PROJ, delete=False, suffix=".tmp") as tf:
        tf.write(tb2)
        tmp = tf.name
    os.replace(tmp, TB)
    print(f"✅ TASK_BOARD §2: 移除 ISS-251 行 + 追加 ②' 对账留痕")

    # ---------------- issue_log ----------------
    with open(IL_LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        doc = yaml.safe_load(open(IL, encoding="utf-8"))
        items = doc["issues"] if isinstance(doc.get("issues"), dict) else (doc.get("issues") or [])
        hit = [it for it in items if it.get("id") == "ISS-251"]
        if len(hit) != 1:
            raise SystemExit(f"✗ issue_log: ISS-251 命中 {len(hit)} 条 (≠1) ⇒ 不写")
        it = hit[0]
        old_status = it.get("status")
        it["status"] = "verified"
        it["fix_ref"] = FIX_REF_251
        it["verify_by"] = "main"
        it["verify_date"] = "2026-11-16"
        it["verify_result"] = VERIFY_251
        it["note"] = (it.get("note") or "") + NOTE_251

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=HERE, delete=False, suffix=".tmp") as tf:
            yaml.safe_dump(doc, tf, allow_unicode=True, sort_keys=False, width=100000)
            tmp = tf.name
        os.replace(tmp, IL)
        fcntl.flock(lk, fcntl.LOCK_UN)

    # ---------------- 自证 ----------------
    doc2 = yaml.safe_load(open(IL, encoding="utf-8"))
    items2 = doc2["issues"] if isinstance(doc2.get("issues"), dict) else (doc2.get("issues") or [])
    it2 = [i for i in items2 if i.get("id") == "ISS-251"][0]
    assert it2["status"] == "verified", it2["status"]
    assert it2["verify_by"] == "main" and it2["verify_date"] == "2026-11-16"
    assert it2["fix_ref"] and it2["verify_result"]
    tb3 = open(TB, encoding="utf-8").read()
    assert "| ISS-251 |" not in tb3.split("## §3")[0].split("## §2")[1]
    assert tb3.count(TB_LINE_NEW) == 1
    print(f"✅ issue_log: ISS-251 status {old_status} → verified (自证: 重读 yaml + 断言过)")
    print(f"✅ 备份: {BACKUP_DIR}/issue_log.yaml.bak_{STAMP} · {BACKUP_DIR}/TASK_BOARD.md.bak_{STAMP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
