#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_1105_iss284_verify_iss282_cont_iss285_open.py
★main (moli) 派活落账 · 2026-11-17 11:0x (cron 775d9893 继续执行后继计划)★

★★**本轮实跑结论 (★全部自己实跑, 不是抄任何交卷报告★)★★ ★★
· ★**`python3 state/advance.py --json` ⇒ internal = []** (★A 段空★)
  · 原因 = ★**hw-lead 名下卡着 ISS-282 (fixing) · sw-lead 名下卡着 ISS-284 (fixing) ⇒ 两个名额都被占★**
  · ★**ISS-284 的会话其实已经交卷完成 (10:34) 但 issue_log 没落状态 ⇒ 僵尸 fixing★**
· ★**ISS-284 (sw-lead) 本机独立复验 (★自己实跑★)**:
  · `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0 · R1~R7 全过** (★R6 已换成「台账链头」口径★)
  · `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=0 · SELFTEST 22/22** (★REV-16~REV-21 六条反向全抓到★)
  · `python3 SW/tools/timing_check.py` ⇒ **rc=1 · 68/71** (★3 条红★)
  · `python3 HW/check_step1_parts_spec.py` ⇒ **rc=0 · 8/8**
  · `python3 HW/check_onepass_preflight_coverage.py` ⇒ **rc=1** (★P5 两探针过期 + P6 三个基线过期★)
  · ★**受保护 5 件**: 板 `611b869e…` ✅ / `.kicad_pro` `3e504d2b…` ✅ (★逐字节不变★) ·
    网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…` ★**= 落表台账 §16.2 登记的「落表后」值 ⇒ 是 09:58 授权落表 (A1/A2) 的正常后果, 不是本单弄的★**
  · ⇒ ★**判定 pass (★ISS-284 自己的范围: SW 台账 hard_protected 合法改板机制 = 绿 + 反向 22/22 + 板两件没动★)**
    ★**但那 3+2 条红要如实记: 它们【不属于 ISS-284 的范围】⇒ 已分派: 3 条红 → 新开 ISS-285 (sw-lead) · 2 条红 → ISS-283 §⑩ (hw-lead)★**
· ★**ISS-282 (hw-lead) = 僵尸 fixing**: 会话 `agent:hw-lead:subagent:169ee40f` 10:04~10:22 `abortedLastRun=true` (★网关重载掐的★)
  · 盘上 3 件交付物已在 (根因订正页 20128 B / 机器闸 39479 B / 作业包 §6.2 追加行 L388) ⇒ ★**但机器闸主模式 rc=1 (3 条红) + selftest 8/10 + 交卷单只有骨架 2617 B + 分片没有 iss282★**
  · ★**main 本机实查 3 条红的根因 (★已写进续做任务书, 不用 agent 从零重查★)**:
    ① D2/D3 = `find_pad(board, "R_SER_FSIN.1", "1")` ⇒ ★**ref 带了脚号后缀 ⇒ 永远匹配不上** ⇒ 实测 `find_pad(b,"R_SER_FSIN","1")` 返回 (93.300,46.600) ✅ / `find_pad(b,"R_SER_FSIN.1","1")` 返回 None ❌
    ② D5 = `landing_after_md5()` 用 `find("前后对照")` 取【第一个】匹配 ⇒ ★**命中 L204~L207 那张旧表 (c78f9912…) 而不是 §16.2 (L1270~1274, 落表后 2f17650c/6ea65fec/ea5f4f58)** ★
    ③ selftest 8/10 = 沙盒复制同一份板 + 同一份台账 ⇒ 同样 3 红 ⇒ ⑩ 正向对照也不绿
  · ⇒ ★**本脚本把 ISS-282 保持 fixing + 追加实况 note + 更新 dispatched_at (★续做重派, 不是新单★)★**
· ★**ISS-283 (hw-lead, open) = 排队**: ★**hw-lead 名额被 ISS-282 占着 ⇒ 本轮不派** ★ ⇒ ★**任务书已补 §⑩ (追加式): land_v_values --selftest 崩 / preflight P5+P6 两条红 / 验收 rc 必须落表后重跑 / SW 那条红归 ISS-285★**

★★**本脚本做的事 (边界写死)★★ ★★
· ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` (★flock + 锁内重读 + tmp/os.replace 原子写★)★**
· ★**ISS-284: fixing → verified** (★fix_ref / verify_by=main / verify_result=pass / verify_date=2026-11-17 / verify_note=本机复验原文★)★
· ★**ISS-282: 保持 fixing** (★追加 note: 僵尸实况 + main 的 3 条红根因 + 续做任务书路径 + dispatched_at 更新★)★
· ★**ISS-283: 保持 open** (★追加 note: 排队原因 + §⑩ 追加块已写进任务书★)★
· ★**新开 ISS-285** (★owner=sw-lead · medium · due 2026-11-19 · status=open · task_brief = 任务书全文★)★
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM / 任何 agent 的分片 / 决策页 / PROJECT_TRACKER §0★**
· ★**零外发 · 零采购 · 不替老板拍板★**
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"
NOW = "2026-11-17 11:0x"

BR282C = os.path.join(HERE, "dispatch_briefs", "ISS-282_hw_fsin_rootcause_correction_cont1.md")
BR285 = os.path.join(HERE, "dispatch_briefs", "ISS-285_sw_landing_after_judgment_alignment.md")


def atomic_write(path: str, data) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="." + os.path.basename(path) + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def read_text(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


def main() -> int:
    for p in (BR282C, BR285):
        if not os.path.exists(p):
            raise SystemExit("★brief 缺失 ⇒ 拒绝落账: %s" % p)
    brief282c = read_text(BR282C)
    brief285 = read_text(BR285)

    shutil.copy2(IL, IL + ".bak_20261117_1105_iss284verify_cont282_open285")
    shutil.copy2(DL, DL + ".bak_20261117_1105_iss284verify_cont282_open285")

    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)

        # ---------------- issue_log ----------------
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        issues = il["issues"]
        by_id = {i.get("id"): i for i in issues}

        # ① ISS-284 (sw-lead) → verified (★若兄弟 job 已落 verified ⇒ 不重复签, 只补独立复核 note★)
        i284 = by_id["ISS-284"]
        if i284.get("status") == "verified":
            # ★兄弟 job (cron fb67af40) 已在 11:0x 落 verified ⇒ 本脚本【不重复签】⇒ 只补 main 的独立复核证据★
            i284["note"] = str(i284.get("note") or "") + (
                "\n★**2026-11-17 11:0x (cron 775d9893) 第二双眼睛独立复核 (★自己实跑, 不抄交卷报告, 也不重复签 verified★)**:\n"
                "· `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0 · R1~R7 全过** (★R6 = 落表台账链头口径★)\n"
                "· `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=0 · SELFTEST 22/22** (★REV-16~REV-21 六条反向全抓到★)\n"
                "· `python3 SW/tools/timing_check.py` ⇒ **rc=1 · 68/71** · `python3 HW/check_onepass_preflight_coverage.py` ⇒ **rc=1** (★P5 ×2 + P6 ×3★)\n"
                "· ★**受保护 5 件**: 板 `611b869e13518c3c023fb178f91a0075` ✅ · `.kicad_pro 3e504d2be83152e337949723e909be1b` ✅ (★逐字节不变★) · "
                "网表 `2f17650cfbef48d5efd71821505c3343` · 脚表 `6ea65fecdf95902e47330083d140d455` · BOM `ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd` "
                "★**= 落表台账 §16.2 (L1270~L1274) 登记的「落表后」值 ⇒ 是 09:58:16 授权落表 (A1=V-3=E / A2=V-4=680) 的正常后果, 不是本单弄的★**\n"
                "⇒ ★**独立复核结论 = 同意 pass** ★\n"
                "★**★那 5 条红【不属于 ISS-284 的范围】(★是授权落表后判据源没跟上★) ⇒ 已分派**:\n"
                "· `SW/tools/timing_check.py` 3 条红 (★网表锚点 ×2 + F4' 期望 ×1★) ⇒ ★**新开 ISS-285 (owner=sw-lead)**★\n"
                "· `HW/check_onepass_preflight_coverage.py` P5+P6 ⇒ ★**并进 ISS-283 (owner=hw-lead) 的任务书 §⑩ 追加块**★\n"
                "· `state/land_v_values.py --selftest` rc=1 (★崩: RuntimeError「旧值出现 0 次」⇒ V-3/V-4 已落过表★) ⇒ ★**并进 ISS-283 §⑩.1**★"
            )
        else:
            assert i284.get("status") == "fixing", "★ISS-284 状态既不是 fixing 也不是 verified ⇒ 拒绝落账: %s" % i284.get("status")
            i284["status"] = "verified"
            i284["fix_ref"] = (
                "HANDOFF/2026-11-17_sw-lead_ISS284_hard_protected合法改板机制.md (22592 B · B1~B6 齐全) · "
                "SW/SW_MD5_BASELINE_LEDGER.md §1 锚点 reboard 机制段 + §3 追加留痕行 (纯追加, 老字零删除) · "
                "SW/tools/check_demo_panel_spec.py (R6 判据 + REV-16~REV-21 六条反向用例) · "
                "state/fragments/sw.yaml (走 frag_write.py 原子写)"
            )
            i284["verify_by"] = "main"
            i284["verify_result"] = "pass"
            i284["verify_date"] = TODAY
            i284["verify_note"] = (
                "★**main 2026-11-17 10:5x~11:0x 独立复验 (★自己实跑, 不抄交卷报告★)**:\n"
                "· `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0 · R1~R7 全过** (★R6 = 「落表台账链头」口径★)\n"
                "· `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=0 · SELFTEST 22/22** (★REV-16~REV-21 六条反向全抓到: "
                "只改 md5 无单号→红 / 台账查不到→红 / 链头不唯一→红 / 链断→红 / 只改板不动 .kicad_pro→红 / 四项齐全→绿★)\n"
                "· `python3 SW/tools/timing_check.py` ⇒ **rc=1 · 68/71** (★3 条红★)\n"
                "· `python3 HW/check_step1_parts_spec.py` ⇒ **rc=0 · 8/8**\n"
                "· `python3 HW/check_onepass_preflight_coverage.py` ⇒ **rc=1** (★P5 两探针过期 + P6 三个基线过期★)\n"
                "· ★**受保护 5 件 md5**: 板 `611b869e13518c3c023fb178f91a0075` ✅ · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ✅ "
                "(★逐字节不变 ⇒ 「板只改一次」铁律未破★) · 网表 `2f17650cfbef48d5efd71821505c3343` · 脚表 `6ea65fecdf95902e47330083d140d455` · "
                "BOM `ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd` ★**= 落表台账 §16.2 (L1270~1274) 登记的「落表后」值 ⇒ 是 09:58:16 授权落表 (A1=V-3=E / A2=V-4=680) 的正常后果, 不是本单弄的★**\n"
                "★**⇒ 判定 pass (★本单范围 = SW 台账 hard_protected 合法改板机制: 绿 + 反向 22/22 + 板两件没动 + 分片 grep iss284 = 8 处★)**\n"
                "★**★如实记: 那 5 条红【不属于 ISS-284 的范围】(★是授权落表后判据源没跟上★)⇒ 已分派**:\n"
                "· `SW/tools/timing_check.py` 3 条红 (★网表锚点 ×2 + F4' 期望 ×1★) ⇒ ★**新开 ISS-285 (owner=sw-lead)**★\n"
                "· `HW/check_onepass_preflight_coverage.py` 2 条红 (★P5 ×2 + P6 ×3★) ⇒ ★**并进 ISS-283 (owner=hw-lead) 的任务书 §⑩ 追加块**★\n"
                "· `state/land_v_values.py --selftest` rc=1 (★是崩不是红: RuntimeError「旧值出现 0 次」⇒ V-3/V-4 已落过表★) ⇒ ★**并进 ISS-283 §⑩.1**★"
            )

        # ② ISS-282 (hw-lead): 保持 fixing + 追加实况 note + dispatched_at
        i282 = by_id["ISS-282"]
        assert i282.get("status") == "fixing", "★ISS-282 状态不是 fixing ⇒ 拒绝落账: %s" % i282.get("status")
        i282["dispatched_at"] = TODAY
        i282["note"] = str(i282.get("note") or "") + (
            "\n★**2026-11-17 11:0x (cron 775d9893) 续做实况 (★本 job 【没有】重复派 hw-lead★)**\n"
            "★**派活方 = 兄弟 job `cron fb67af40` (ARS45 队列自动派活) 于 11:0x 派出**: session `agent:hw-lead:subagent:e1153379-0690-4a1b-b8d3-09b793df4412` · "
            "taskName=`queue_iss282_cont` · ★**status=running** ⇒ ★**同一 agent 同时只允许一个写会话 ⇒ 本 job 不再派第二条 (★派了就是两条并发写分片 = R18 丢数据★)** ⇒ "
            "★**本 job 做的是【第二双眼睛】**: ① 写了续做任务书 `state/dispatch_briefs/ISS-282_hw_fsin_rootcause_correction_cont1.md` (★已过 `state/check_brief_commands.py --brief-file` rc=0★) "
            "② 往原任务书 `ISS-282_hw_fsin_rootcause_correction.md` 追加了 ★附3★ 块 (★追加式, 老字一字未删★) ③ ★**已用 `sessions_send` 把【第三个坑】发给在飞会话★**\n"
            "★**会话死因**: `agent:hw-lead:subagent:169ee40f-64eb-4cda-b473-eb9059efdfc5` 10:04~10:22 · `abortedLastRun=true` (★网关重载掐的★) · "
            "★**transcript 最后一句**: 「Diagnosed: my landing-ledger window matched an older section (line 108/204) instead of §16.2 (line 1270), "
            "and the anchor's pad refs need splitting. Let me fix both.」 ⇒ ★**它自己已经定位到两个病灶, 还没改完就被掐了**\n"
            "★**盘上现状**: 根因订正页 `HW/PCB/FSIN_OUT_ROOTCAUSE.md` 20128 B (10:16) ✅ · 机器闸 `HW/check_fsin_rootcause.py` 39479 B (10:19) ⚠️"
            "(★主模式 rc=1 · 3 条红 · `--selftest` 8/10★) · 作业包 §6.2 追加行 L388 (★老 S8 行 L387 逐字仍在 ⇒ 老字零删除 ✓★) · "
            "★**交卷单只有骨架 2617 B (B1~B6 全「待填」)** ⇒ ★**分片没有 iss282 (hw.yaml mtime 09:22)**\n"
            "★**main 本机实查的 3 条红根因 (★已写进续做任务书, 不用从零重查★)**:\n"
            "① D2/D3 = `find_pad(board, \"R_SER_FSIN.1\", \"1\")` ⇒ ★**ref 带了脚号后缀 ⇒ 永远匹配不上** ★ ⇒ 实测 `find_pad(b,\"R_SER_FSIN\",\"1\")` ⇒ "
            "('R_SER_FSIN','1','FSIN_OUT', 93.3, 46.6, ...) ✅ / `find_pad(b,\"R_SER_FSIN.1\",\"1\")` ⇒ None ❌ ⇒ ★**修法二选一: 页面锚点把脚号单列, 或调用点先 split('.') ⇒ 不许放宽 find_pad 去「猜」★**\n"
            "② D5 = `landing_after_md5()` 用 `landing_txt.find(\"前后对照\")` 取【第一个】匹配 ⇒ ★**命中 L204~L207 那张旧表 (基线 c78f9912… / 产物 13f59a43dbd3…) "
            "而不是 §16.2 (L1270~1274: 落表后 = 网表 2f17650c… / 脚表 6ea65fec… / BOM ea5f4f58…) ⇒ 假红** ★ ⇒ ★**修法: 取该文件最新一条落表记录 ⇒ 不许把允许集写死成常量★**\n"
            "③ `--selftest` 8/10 = ★**沙盒复制同一份板 + 同一份台账 ⇒ 同样 3 红 ⇒ ⑩ 正向对照也不绿** ⇒ ★**修完 ①② 应回 10/10 ⇒ 自测必须端到端跑真板★**\n"
            "★**⇒ 续做任务书: `state/dispatch_briefs/ISS-282_hw_fsin_rootcause_correction_cont1.md` (★已过 `state/check_brief_commands.py --brief-file` rc=0★)** ⇒ "
            "★**派活口径 = 从盘上 3 件交付物接着做 (不许从零重做), 只交: 闸修绿 + 交卷单填满 B1~B6 + 分片** ★"
        )

        # ③ ISS-283 (hw-lead): 保持 open + 追加排队 note
        i283 = by_id["ISS-283"]
        assert i283.get("status") == "open", "★ISS-283 状态不是 open ⇒ 拒绝落账: %s" % i283.get("status")
        i283["note"] = str(i283.get("note") or "") + (
            "\n★**2026-11-17 11:0x (cron 775d9893): 仍排队 (★hw-lead 名额被 ISS-282 占着 ⇒ 本轮不派★)**\n"
            "★**任务书已追加 §⑩ (★追加式, 老字一字未删★)**: ⑩.1 `state/land_v_values.py --selftest` rc=1 (★是崩不是红: RuntimeError「旧值出现 0 次」⇒ V-3/V-4 已落过表★) · "
            "⑩.2 `HW/check_onepass_preflight_coverage.py` rc=1 (★P5: B17_DNP_43='零标记 40 颗' / B03_ULDO_S28_PAD3='18 条缺陷' 过期; P6: 三个基线 md5 过期 ⇒ 走 H-1 四项重锚, 出处 = 落表台账 §16★) · "
            "⑩.3 验收 rc 必须在三件落表【之后】重跑 (★不许拿落表前的 rc 交卷★) · ⑩.4 `SW/tools/timing_check.py` 那 3 条红归 ISS-285 (sw-lead) ⇒ 不许 hw-lead 碰 SW 文件\n"
            "★**⇒ 本单下一轮派 (★hw-lead 名额空出来就派★) ★"
        )

        # ④ 新开 ISS-285 (owner=sw-lead)
        assert "ISS-285" not in by_id, "★ISS-285 已存在 ⇒ 拒绝重复开单★"
        i285 = {
            "id": "ISS-285",
            "title": (
                "★★[主线内·SW 侧·判据口径收口·内部活] ★★【落表之后: SW 侧三道判据过期】★★ "
                "★**`SW/tools/timing_check.py` rc=1 (68/71 · 3 条红) = 授权落表后【判据源不一致】** ★ "
                "⇒ ① 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 ② 网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 "
                "③ F4' 实读: BAT_DET 三颗全 DNP (★落表后已改必装 ⇒ 期望过期★) ★ "
                "★**根因 = 同一事实两个判决源: `check_demo_panel_spec.py` R6 走【落表台账链头】(绿) vs `timing_check.py` 读【SW 台账锚点冻结值】(红)** ★ "
                "★⇒ 修法必须落在「两个判据源同源」上, 不许靠放宽判据消红★"
            ),
            "severity": "medium",
            "owner": "sw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-19",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": (
                "★**2026-11-17 11:0x (cron 775d9893 继续执行后继计划) 新开** ★\n"
                "★**依据 = main 2026-11-17 10:5x 本机实跑 (★不抄任何交卷报告★)**: "
                "`python3 SW/tools/timing_check.py` ⇒ **rc=1 · SELFTEST 68/71** (★3 条红★) ⇒ 根因逐条定位到行号级 ⇒ "
                "★**网表锚点两条红** = `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块 `source_ledger.entries[]` 的网表那一条 `md5` 还停在 **ISS-257 那跳 `e06c1dd6…`** "
                "⇒ 而盘上已是 09:58:16 授权落表 (A1=V-3=E / A2=V-4=680) 后的 `2f17650c…` ⇒ `timing_check.py` L244~L247 「盘上真源 md5 ≠ 锚点登记 md5」⇒ 判 BAD ⇒ "
                "★**⇒ 看起来像「真源被换了」, 实际是【授权落表后第二个判据源没跟上】★** ⇒ "
                "★**第 3 条红** = F4' 期望还写着「BAT_DET 三颗全 DNP」, 而落表后网表 L182/L183/L184 = `100k`/`60k`/`100nF` **必装** ⇒ 期望过期 ★\n"
                "★**★开工前置 (硬)**: ★**ISS-283 (hw-lead) 的三件落表 (A3=V-2=1 + W-4 `Q_PG` pad1↔pad3 + G-5 亮度档) 一落, 网表/脚表/BOM md5 会【再变一次】** ⇒ "
                "★⇒ 本单分两段: ISS-283 未落 verified ⇒ 只交【只读分析 + 方案页 + 自测设计】(不许改锚点/不许改期望); ISS-283 已落 ⇒ 做全套 ⇒ 任务书 §③ 已写死★\n"
                "⇒ ★**任务书 `state/dispatch_briefs/ISS-285_sw_landing_after_judgment_alignment.md`** (★已过 `state/check_brief_commands.py --brief-file` rc=0★) ★\n"
                "★**边界**: 零写板 · 零落表 · 不许动 ISS-275 已跑通的链头逻辑 · 不许放宽 fail-closed 三条 · 不碰 `HW/` / `MECH/` 文件与分片 · 零外发 · 不自签 issue_log · 不替老板拍板 ★"
            ),
            "dispatched_at": None,
            "task_brief": brief285,
        }
        issues.append(i285)

        atomic_write(IL, il)

        # ---------------- dispatch_log ----------------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        entries = dl.get("entries")
        if entries is None:
            entries = []
            dl["entries"] = entries
        entries.append({
            "issue": "ISS-282",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": (
                "★**续做重派第 1 次 (★2026-11-17 10:22 会话被网关重载掐断: `abortedLastRun=true` ⇒ 盘上 3 件交付物已在 "
                "(根因订正页 20128 B / 机器闸 39479 B / 作业包 §6.2 追加行 L388) 但【机器闸主模式 rc=1 · 3 条红】+ 交卷单只有骨架 2617 B + 分片无 iss282★) ⇒ "
                "★**从盘上继续, 不要从零重做**★ · ★**main 已把 3 条红的根因定位到行号级**★ "
                "(① find_pad 的 ref 带了脚号后缀 ⇒ 永远匹配不上 ② landing_after_md5 取了台账里第一张「前后对照」旧表而不是 §16.2 ③ selftest 沙盒同 3 红) ⇒ "
                "★**照这个改**★ · ★**续做纪律**: 交卷单骨架已在 ⇒ 直接填 · 长任务 nohup 后台 · 单条 exec ≤120 秒 · 每 10 分钟写盘 · 分片 frag_write.py + grep 校验★"
            ),
            "job": "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 11:0x 派出并在飞 (session e1153379) ★ · ★本 job (775d9893) 只补了任务书 cont1 + 原任务书 ★附3★ 追加块 + sessions_send 补充第三个坑 (★不重复派同一 agent★)",
        })
        entries.append({
            "issue": "ISS-285",
            "agent": "sw-lead",
            "at": TODAY,
            "brief": brief285,
            "job": "cron 775d9893 (ARS45 继续执行后继计划) · 新开单 (★等 hw-lead 名额或 sw-lead 名额空出来再派★)",
        })
        atomic_write(DL, dl)
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    print("★落账完成: ISS-284 fixing→verified · ISS-282 保持 fixing (续做重派) · ISS-283 保持 open (排队 + §⑩) · 新开 ISS-285 (owner=sw-lead, open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
