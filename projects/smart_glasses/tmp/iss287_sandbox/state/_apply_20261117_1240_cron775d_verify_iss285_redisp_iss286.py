#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_1240_cron775d_verify_iss285_redisp_iss286.py
★main (moli) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-17 12:4x★
★★**两件事 (边界写死)★★ ★★
① ★**ISS-285: fixing → verified** (★verify_by = main ⇒ 签字是 main 的活★)
② ★**ISS-286: 保持 fixing + 续做重派留痕** (★半落地僵尸 · 不是新单★)

★★**本轮实跑结论 (★全部自己实跑, 不抄交卷报告★)★★ ★★
· ★**advance.py --json ⇒ internal = []** (★三个名额全被 fixing 占着: ISS-283/hw-lead · ISS-285/sw-lead · ISS-286/mech-lead★)
  ⇒ ★**但盘面实况 ≠ 名单**: hw-lead 的 ISS-283 **正在跑** (会话 `adfd437a` status=running) · sw-lead 的 ISS-285 **已交卷** ·
  mech-lead 的 ISS-286 **是半落地僵尸** ⇒ ★**本轮真正该动的就是这两条** ★
· ★**ISS-285 (sw-lead) 会话 `agent:sw-lead:subagent:a2da41cd` 于 12:00:36 done** ⇒ 盘上 4/4 交付物齐全 ⇒ ★**main 复验通过** ★
  ① `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** (★R1~R7 全过★) ★
  ② `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=0 · 22/22** ★
  ③ `python3 SW/tools/timing_check.py` ⇒ **rc=1 · 68/71** (★3 条红★) ⇒ ★**这是【情形一】的预期值★
     (ISS-283 未落 verified ⇒ 补丁不套用 ⇒ 判据一字未动 ⇒ 红的就是原来那 3 条)★ ★
  ④ ★**反向用例自测器实跑**: `SW/patches/ISS-285_sw_judgment_alignment/sbx_iss285_reverse_cases.py` ⇒ **rc=0 ·
     5 条用例总判定 ✅ 全符合** (①伪造 md5 ②台账四项不齐 ③链头不唯一 ④BAT_DET 改回 DNP ⑤正向对照·期望红组 vs 实际红组逐条一致)★ ★
  ⑤ ★**受保护件实读**: 板 `611b869e…` (mtime 仍 `2026-11-06 07:07:17`) · `.kicad_pro` `3e504d2b…` ·
     `SW/tools/timing_check.py` mtime `2026-11-16 18:32` (★sw-lead 没动·情形一正确★) ·
     `SW/SW_MD5_BASELINE_LEDGER.md` mtime `2026-11-17 10:30` (★同上★) ★
  ⑥ ★**网表/脚表/BOM 现值 `37f62ac3…`/`a4270120…`/`5d02bece…` ⇒ 不是 sw-lead 动的**
     (★三件 mtime = 2026-11-17 12:30:22 ⇒ 晚于 sw-lead 交卷 12:00:36 ⇒ 是 ISS-283 (hw-lead) 的授权落表★) ★
  ⑦ 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口.md` = 30194 B + 方案页 19041 B ·
     `SW/patches/ISS-285_sw_judgment_alignment/` (套用器 26289 B + 反向自测器 12493 B) · `fragments/sw.yaml` grep iss285 = 6 ★
  ⇒ ★**判定 pass (★情形一交付: 方案页 + 可套用补丁 + 反向用例 + need 登记★)★**
  ⇒ ★**后续 need 已登记**: `iss285_sw_apply_after_iss283_verified` ⇒ ★**等 ISS-283 落 verified 后套用 ⇒ 套完 timing_check 期望 rc=0·72/72**★

· ★**ISS-286 (mech-lead) 是半落地僵尸**: 会话 `agent:mech-lead:subagent:a6a8ca76` (11:41→12:13 · status=done ·
  abortedLastRun=true) ⇒ transcript 末条 = 12:07:25 一段被 abort 的 thinking ⇒ ★**停在设计阶段, 连代码都没开始写**★ ★
  ⇒ ★**盘面实况 (main 12:3x 实测)**: `MECH/check_board_frame_coords.py` md5 `92f4eebb…` mtime `Nov 17 06:57` ⇒ **一字未动** ·
     `MECH/patches/` 目录不存在 · 交卷单 **867 B 骨架** (B1~B6 全「（施工中）」) · `fragments/mech.yaml` grep iss286 = **0** ⇒ **分片零写** ★
  ⇒ ★**⇒ 已派【续做重派 cont1】**: 任务书 `state/dispatch_briefs/ISS-286_mech_frame_gate_ledger_caliber_cont1.md` (6648 B ·
     派活前过 `python3 state/check_brief_commands.py --brief-file …` ⇒ **rc=0 零告警**) · 会话 `agent:mech-lead:subagent:ea2ee0d7` ★

★★**★main 12:3x 顺带查实的一件硬证据 (★写进 cont1 任务书★)★★ ★★
★**「硬写基线」的病在 40 分钟内发作了两次**: ISS-283 于 12:1x / 12:2x 连落两次表 ⇒ 网表 md5 `2f17650c…`→`87f2f792…`→`37f62ac3…`
★**⇒ C4 那三条硬写基线已过期两轮 (不是「下次会红」, 是「已经红了三遍」)★** ★
★**★而且 main 已把先例验通 ⇒ cont1 直接给答案不用 mech-lead 自己推★**:
★**用 `MECH/check_demo_struct_truth.py` 的 ISS-273 台账解析器 (`ledger_state`) 指向当前真台账实跑** ⇒ ★
  网表 head=`37f62ac3f0b8` = 盘上 · 脚表 head=`a4270120454a` = 盘上 · BOM head=`5d02bece9477` = 盘上 ⇒ ★**三条全 MATCH · why=(none)·producer=ISS-283** ★
⇒ ★**⇒ 【台账为准】口径此刻就是绿的 ⇒ 本单是「把口径搬进 C4」, 不是「追新的基线数字」★** ★

★★**本脚本做的事 (边界写死)★★ ★★
· ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` (★flock + 锁内重读 + tmp/os.replace 原子写 + 先备份★)★**
· ★**ISS-285: fixing → verified** (★fix_ref / verify_by=main / verify_result=pass / verify_date / verify_note★)★
· ★**ISS-286: status 保持 fixing** + note 追加僵尸实况 + dispatched_at 刷新 + task_brief 换头 + dispatch_log 追加 1 条 (续做重派)★
· ★**其它 issue 一条不动** ★
· ★**不碰板 / 网表 / 脚表 / BOM / 台账 / 任何 agent 的分片 / 决策页 / outbox / PROJECT_TRACKER §0****
· ★**零外发 · 零采购 · 不替老板拍板****
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
STAMP = "2026-11-17 12:4x (cron 775d9893 继续执行后继计划)"

# ══════════════════════════════════════════════════════════════════════════
# ① ISS-285 · fixing → verified
# ══════════════════════════════════════════════════════════════════════════
V285_NOTE = (
    "★**main 2026-11-17 12:4x 本机独立复验 (★cron 775d9893「继续执行后继计划」· 自己实跑, 不抄交卷报告★)**: "
    "① `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** (★R1~R7 全过★) "
    "② `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=0 · 22/22** "
    "③ `python3 SW/tools/timing_check.py` ⇒ **rc=1 · SELFTEST 68/71** (★3 条红★) ⇒ ★**这是【情形一】的预期值**: "
    "ISS-283 尚未落 verified ⇒ 按任务书 §③ 不套用补丁 ⇒ 判据与锚点一字未动 ⇒ 红的就是原来那 3 条 "
    "(★**不是新红的**·★`SW/tools/timing_check.py` mtime 仍 2026-11-16 18:32 · "
    "`SW/SW_MD5_BASELINE_LEDGER.md` mtime 仍 2026-11-17 10:30 ⇒ sw-lead 确实没碰这两个文件★)★ "
    "④ ★**反向用例自测器实跑** `SW/patches/ISS-285_sw_judgment_alignment/sbx_iss285_reverse_cases.py` ⇒ **rc=0 · "
    "5 条用例总判定 ✅ 全符合** (①伪造 md5 ②台账四项不齐 ③链头不唯一 ④BAT_DET 三颗改回 DNP ⑤正向对照 ⇒ "
    "每条的【期望红组 vs 实际红组】逐条一致)★ "
    "⑤ ★**受保护件实读**: 板 `611b869e13518c3c023fb178f91a0075` (★mtime 仍 `2026-11-06 07:07:17.362193413`★) · "
    "`.kicad_pro` `3e504d2be83152e337949723e909be1b` ★ "
    "⑥ ★**网表/脚表/BOM 现值 `37f62ac3f0b8…`/`a4270120454a…`/`5d02bece9477…` ⇒ 不是 sw-lead 动的** "
    "(★三件 mtime = 2026-11-17 12:30:22 ⇒ 晚于 sw-lead 交卷 12:00:36 ⇒ 是 ISS-283 (hw-lead) 的授权落表·"
    "且台账链头与盘上三件逐件 MATCH ⇒ 落表台账是好的★)★ "
    "⑦ 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口.md` = 30194 B · 方案页 19041 B · "
    "`SW/patches/ISS-285_sw_judgment_alignment/` (套用器 26289 B + 反向自测器 12493 B) · "
    "`state/fragments/sw.yaml` grep iss285 = **6** (分片已写) ★ "
    "⇒ ★**判定 pass (★本单自己的范围 = 情形一交付: 只读分析 + 方案页 + 可套用补丁 + 反向用例设计 + need 登记★)★** "
    "★**⇒ 后续 need 已登记**: `iss285_sw_apply_after_iss283_verified` ⇒ ★**等 ISS-283 落 verified 后套用 "
    "(`--apply`, 期望修后 md5 `68c4becf…`) ⇒ 套完 `timing_check.py` 期望 rc=0 · 72/72**★ "
    "★**⇒ sw-lead 名额释放 (★但 sw-lead 名下已无 open 待办 ⇒ 本轮不派★)★**"
)

V285_TAIL = (
    "★**2026-11-17 12:4x (cron 775d9893 继续执行后继计划): fixing → verified** ★ "
    "★**sw-lead 会话 `agent:sw-lead:subagent:a2da41cd` 12:00:36 交卷** ⇒ 盘上 4/4 交付物齐全 + 分片已写 "
    "⇒ ★**main 本机独立复验通过 (check_demo_panel_spec rc=0 · selftest 22/22 · 反向用例 5/5 全符合 · "
    "timing_check rc=1·68/71 属情形一预期值 · 板/.kicad_pro 逐字节不变)** ⇒ **sw-lead 名额释放**★ "
    "★**后续: 等 ISS-283 落 verified 后套用补丁 (`iss285_sw_apply_after_iss283_verified`)★**"
)

V285_FIX_REF = (
    "HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口.md | "
    "HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口_方案页.md | "
    "SW/patches/ISS-285_sw_judgment_alignment/apply_iss285_sw_judgment_alignment.py | "
    "SW/patches/ISS-285_sw_judgment_alignment/sbx_iss285_reverse_cases.py"
)

# ══════════════════════════════════════════════════════════════════════════
# ② ISS-286 · 保持 fixing + 续做重派留痕
# ══════════════════════════════════════════════════════════════════════════
V286_NOTE = (
    "\n\n★**2026-11-17 12:4x (cron 775d9893 继续执行后继计划) 半落地僵尸 ⇒ 【续做】重派 (★不是新单·status 保持 fixing★)** ★\n"
    "· ★**僵尸实况 (main 自己查盘 + 读 transcript, 不抄兄弟 job 的报告)**: 子会话 "
    "`agent:mech-lead:subagent:a6a8ca76` (11:41→12:13 · status=done · abortedLastRun=true) ⇒ "
    "transcript 末条 = 12:07:25 一段被 abort 的 thinking ⇒ ★**停在「设计阶段」, 连代码都没开始写**★ ⇒ "
    "★**pid 无残留 ⇒ 无僵尸进程在改盘**★\n"
    "· ★**盘面实况 (main 12:3x 实测)**: `MECH/check_board_frame_coords.py` md5 `92f4eebb7f70c129f20e964cdf7485a0` · "
    "mtime `Nov 17 06:57` ⇒ ★**一字未动 ⇒ 改动零落地**★ · `MECH/patches/` ★**目录不存在**★ · "
    "交卷单 `HANDOFF/2026-11-17_mech-lead_ISS286_坐标归一闸台账化.md` = ★**867 B 骨架** (B1~B6 全「（施工中）」)★ · "
    "`grep -c \"iss286\" state/fragments/mech.yaml` = **0** ⇒ ★**分片零写**★\n"
    "· ★**★决定性新证据 (main 12:3x 实跑, 已写进 cont1 任务书)★**: ★**「硬写基线」的病在 40 分钟内发作了两次**★ ⇒ "
    "ISS-283 于 12:1x / 12:2x 连落两次表 ⇒ 网表 md5 `2f17650c…` → `87f2f792…` → `37f62ac3…` ⇒ "
    "★**C4 那三条硬写基线已过期两轮 ⇒ 不是「下次会红」, 是「已经红了三遍」**★\n"
    "· ★**★而且先例已被 main 验通 ⇒ 本单不必自己推★**: 用 `MECH/check_demo_struct_truth.py` 的 ISS-273 台账解析器 "
    "(`ledger_state`) 指向当前真台账实跑 ⇒ 网表 head=`37f62ac3f0b8` = 盘上 · 脚表 head=`a4270120454a` = 盘上 · "
    "BOM head=`5d02bece9477` = 盘上 ⇒ ★**三条全 MATCH · why=(none) · producer=ISS-283**★ ⇒ "
    "★**【台账为准】口径此刻就是绿的 ⇒ 本单 = 把口径搬进 C4, 不是追新的基线数字**★\n"
    "· ★**续做任务书** = `state/dispatch_briefs/ISS-286_mech_frame_gate_ledger_caliber_cont1.md` (6648 B · "
    "★派活前已过 `python3 state/check_brief_commands.py --brief-file …` ⇒ rc=0 零告警★) ⇒ "
    "★**第一件事 cat 全文 (含原任务书全文路径 + 先例代码位置 + 4 条反向用例 + 必跑清单)****\n"
    "· ★**会话**: `agent:mech-lead:subagent:ea2ee0d7-f4de-457d-a6f1-60bf6a24f8e4` (★cron 775d9893 派出·"
    "★**一个 agent 同时只派 1 条的纪律**: hw-lead 在跑 ISS-283 · sw-lead 本轮不派 ⇒ ★**mech-lead 名额空着才派★**)★\n"
)

V286_HEAD = (
    "★**续做重派 (★11:41~12:13 那一趟会话被 abort ⇒ 盘上几乎什么都没落: 交卷单 867 B 骨架 · 闸脚本一字未动 · "
    "分片零写 ⇒ 从盘上现状继续, 不要从零重做★)** ⇒ "
    "★**完整续做任务书全文 = `state/dispatch_briefs/ISS-286_mech_frame_gate_ledger_caliber_cont1.md` (6648 B) ⇒ 第一件事先 cat 全文**★\n"
    "★**原任务书全文** = `state/dispatch_briefs/ISS-286_mech_frame_gate_ledger_caliber.md` (5233 B · §①~§⑤) ⇒ 也 cat 一遍★\n"
    "★**★main 已替你验通先例, 不要自己创**: 用 `MECH/check_demo_struct_truth.py` 的 `ledger_state`/`ledger_records` "
    "指向当前真台账 ⇒ 三件 head == 盘上 (37f62ac3 / a4270120 / 5d02bece) ⇒ 【台账为准】口径此刻就是绿的 ★\n"
    "★**★剩下的是**: 改 C4 三条基线 → 取值来源改成台账链头 (板/.kicad_pro 两行**保留写死**) → 新增 ≥4 条反向用例 → "
    "跑 `check_board_frame_coords.py` + `--selftest` + `check_demo_struct_truth.py` → 填满 867 B 交卷单骨架 (B1~B6) → "
    "写分片 (`frag_write.py --agent mech-lead` + grep 校验) ★\n"
)


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


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8")) or {}
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        shutil.copy2(IL, IL + ".bak_20261117_1240_cron775d_verify_iss285_redisp_iss286")
        shutil.copy2(DL, DL + ".bak_20261117_1240_cron775d_verify_iss285_redisp_iss286")

        by_id = {it.get("id"): it for it in (il.get("issues") or [])}

        # ── ① ISS-285: fixing → verified ──
        t285 = by_id.get("ISS-285")
        if t285 is None:
            raise SystemExit("★ISS-285 不在 issue_log ⇒ 拒绝落账")
        if t285.get("status") not in ("fixing", "verified"):
            raise SystemExit("★ISS-285 status=%r ⇒ 拒绝落账" % t285.get("status"))
        before285 = t285.get("status")
        t285["status"] = "verified"
        t285["fix_ref"] = V285_FIX_REF
        t285["verify_by"] = "main"
        t285["verify_result"] = "pass"
        t285["verify_date"] = TODAY
        t285["verify_note"] = V285_NOTE
        old = t285.get("note") or ""
        if "12:4x (cron 775d9893 继续执行后继计划): fixing → verified" not in old:
            t285["note"] = (old.rstrip() + "\n" + V285_TAIL).strip()

        # ── ② ISS-286: 保持 fixing + 续做重派留痕 ──
        t286 = by_id.get("ISS-286")
        if t286 is None:
            raise SystemExit("★ISS-286 不在 issue_log ⇒ 拒绝落账")
        if t286.get("status") != "fixing":
            raise SystemExit("★ISS-286 status=%r ⇒ 拒绝落账 (续做重派要求 fixing)" % t286.get("status"))
        t286["note"] = (t286.get("note") or "") + V286_NOTE
        t286["dispatched_at"] = TODAY
        t286["task_brief"] = V286_HEAD + (t286.get("task_brief") or "")

        dl.setdefault("dispatches", []).append({
            "issue": "ISS-286",
            "agent": "mech-lead",
            "at": TODAY,
            "brief": V286_HEAD.strip(),
            "job": ("★派活方 = cron 775d9893 (ARS45 继续执行后继计划) 于 12:4x 派出 · ★上一趟 "
                    "(agent:mech-lead:subagent:a6a8ca76 · 11:41→12:13 · done/abortedLastRun) 是半落地僵尸★ "
                    "⇒ 本条为【续做重派第 1 次】★"),
        })

        atomic_write(IL, il)
        atomic_write(DL, dl)

    print("★ISS-285: %s → verified (fix_ref + verify_note 落账)" % before285)
    print("★ISS-286: 保持 fixing + note 追加 + dispatched_at 刷新 + task_brief 换头 + dispatch_log 追加 1 条 (续做重派)")
    print("★备份: issue_log.yaml.bak_20261117_1240_cron775d_verify_iss285_redisp_iss286")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
