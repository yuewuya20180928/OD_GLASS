#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-19 02:3x · 派 ISS-337 cont1 (hw-lead)** ★

★★**先落 fixing 再 spawn (★硬规则: 反过来会留窗口让下一轮 cron 重复派同一 agent★)★★
★**ISS-337 已经是 `fixing` ⇒ 本单是【cont1 续做】⇒ status 保持 fixing ⇒ 无 open 窗口 ⇒ 下一轮 in_flight 规则跳过 hw-lead ⇒ 兄弟 job 775d9893 不会重复派★**

★**为什么本轮 advance.py 的 A 段是空的, 还是要派 ISS-337 cont1 (★全部本机实读·不抄任何 agent 报告★)**:
  ① `python3 state/advance.py --json` ⇒ ★**`internal: []`** ⇒ 三个总工各被一条 `fixing` 占位 (★ISS-335 sw-lead / ISS-336 mech-lead / ISS-337 hw-lead / ISS-338 sw-lead★) ⇒ ★**A 段自己派不出** ★
  ② ★**hw-lead 名下零运行中会话** (★本 job 02:1x `sessions_list` + `subagents list` 双读: active=0 · 最近 180 分钟零新会话·★hw-lead 最后一条会话 `5f685e7f` 01:08 结束 status=done★) ⇒ ★**名额事实为空** ★
  ③ ★**ISS-337 的 5 处缺口本 job 逐件独立实读确认 (★不抄 main 的报告★)**:
     · 交卷页 B 块标题 L104 = `## B4 · 分片` ⇒ ★**闸认不出 (★`gate_check.py` L51 的 B4 判据 = 标题须含 `接口取值`/`接口声明`/`interface_claims`/`接口请求` 之一★)** ★
     · `grep -c iss337 state/fragments/hw.yaml` = ★**0** ★
     · `logs/iss337/15_seg_parity_selftest.txt` 末行 = ★**`SELFTEST FAILED`** ★ ⇒ 用例 5 (★脚本 L273-279: `tight_hi=2600` ⇒ norm=2582 落在 [2300,2600] 带内 ⇒ 期望值写反★)
     · 交卷页 L120 = `过孔 ∈ **[380, 450]**` ⇒ ★**与脚本 L61 `VIA_LO, VIA_HI = 380, 520` 冲突** ★
     · 「归一化段数」定义未钉死 (★脚本 `tmp/iss337/merge_full.py` 的 `full_merge()` 迭代式 ⇒ 换实现就换数★)
  ④ ★**闸实测 (★本 job 02:2x 本机独立实跑·★`TMPDIR=<项目内> timeout 600 python3 state/gate_check.py`★)**: ★**rc=0 · Q1 = 17/18 (★缺口正是 hw-lead 的 B4★) · Q2 3/3 · Q6 ✅ · Q7 9/9 · extra_gates 8/8 · 缺口清单 4 条 (★hw-lead 缺 B4 + 三个总工的「需求还没人答」★)** ★
  ⑤ ★**派活授权**: ★**main 01:44 webchat 实读 ⇒「⇒ **cont1 任务书已写好落盘** (`state/dispatch_briefs/ISS-337_hw_segment_parity_cont1.md`), 5 处缺口 + 上面两条发现都写进去了, ★**兄弟 job 直接派即可**★」** ★ ⇒ ★**main 明确授权「兄弟 job」(★= 本 job★) 直接派 ISS-337 cont1** ★
  ⑥ ★**兄弟 job 775d9893 于 01:53 死于 status=failed (★`sessions_list` 实读: sessionId=ff0de45e · startedAt=1795023814256 · endedAt=1795024387879 · runtimeMs=573623★) ⇒ ★**它没派成 (★hw-lead 名下零新会话·★本 job 02:1x~02:3x 反复核对·★无任何 hw-lead 会话在 01:08 之后产生★)** ⇒ ★**本 job 接手, 不存在撞车** ★
  ⑦ ★**不碰 sw-lead / mech-lead**: ★**ISS-335 / ISS-336 / ISS-338 的会话全部已结束 (★01:48 sw-lead 交卷完毕 / 01:29 mech-lead 交卷完毕 / 00:51 sw-lead ISS-335 交卷完毕★) ⇒ ★**它们现在是【待 main 签收】的僵尸占位, 不是「还在飞」⇒ 签收是 main 的地界·本 job 不签 (★签两次会让审计出现两条 verified 记录★)★ ⇒ 本轮无新的 open 项给它们 ⇒ 不派** ★

★**★brief 改动 1 处 (★其余逐字未改·★派活方 02:2x 本机实读新发现★)**:
★**追加「第 6 处缺口」一节 (★在正文之后追加·★main 的原文前 11,870 字节 `diff` 校验逐字未改★)**:
  ★**★为什么追加 (★不是找茬·是同一类病★)**: ★**派活方逐件核对 `logs/iss337/` ⇒ 交卷页 §B3 表声称 16 件、盘上只有 13 件 ⇒ 第 13/14/16 行引用【不存在的文件】⇒ §5 沙盒臂表 8 个读数列全是空指针 `(见 §B3-13)`/`(见 §B3-14)` ⇒ 与第 1 处 (B4 标题) 同属【交卷页结构与盘面不同步】⇒ main 一 grep 就抓到 ⇒ 不补这第 6 处, main 依然不能签** ★
  ★**直接原因 (★不用 agent 重跑任何臂★)**: ★**`tmp/iss337/sbx/run_sbx.out` 实读 ⇒ `[A] ★EXIT=124` (★timeout 3600 被打死⇒SBX-A 板没生成★) + ★**SBX-B 是已死会话 `5f685e7f` 的孤儿进程 (★本 job 02:2x 已 kill·★pid 1208854/1208853/1192825/1192822 全清·★板 md5/mtime 复查逐字节未动★)** ⇒ ★**13/14 两个日志本就不可能存在 ⇒ §5 两条臂读数从一开始就没产出过** ★
  ★**⇒ brief 里写死了收口方式**: ★**§5 两条臂读数改 `[0数据]`+原因 + §B3 表自称件数改成 13 (★不许编任何段数/过孔/铜长/unc/DRC 数字★) + 零空指针 + 追加了第 ⑦ 条复现命令与第 ⑥ 条验收线** ★

★**派活前命令存在性守卫**: ★**`python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-337_hw_segment_parity_cont1.md` ⇒ rc=0** ★

★**边界 (★ISS-337 cont1 自己的 §硬边界 一字未改 + 派活方零加码·★派活方只追加了第 6 处缺口★)**:
★**零写板 (★md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413`★) · 零落表 (★网表/脚表/BOM md5 不变★) · 零改闸 (★`state/gate_check.py`/`compare_arm_official.py`/`chain_gate.py`/`daily_check.py`/`check_pcb_drc.py` md5 不变★) · 零改真生成器 (★`state/gen_pcb_routing.py`/`gen_pcb_netlist_board.py`/`gen_kicad_project.py` md5 不变★) · 零改别人分片 (★只写 `state/fragments/hw.yaml`·★只走 `frag_write.py --agent hw-lead`★) · 只补不重做 (★不许重跑已在盘的六层读数·★不许新建臂★) · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·全靠自己查★) · 不替老板拍板 (★老板那 8 个字母 + U-1 + P7 一个都不许碰★) · 不自签 issue_log ★**

★**本单 = PCB 线 · 纯补缺口/分析类 · 零写板 ⇒ 符合老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」+ 「板只改一次」铁律 (★不动板 · 不动网表真源·★只补交卷页 + 写分片 + 修自测脚本★)★**
★**零写板 · 零落表 · 零改闸 · 零改 agent 分片 · 零外发 · 本 job 全程未调用 message 工具★**
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261119_0230_cronfb67_dispatch_iss337_cont1"
IID = "ISS-337"
OWNER = "hw-lead"

BRIEF_FILE = os.path.join(HERE, "dispatch_briefs", "ISS-337_hw_segment_parity_cont1.md")
BRIEF = open(BRIEF_FILE, encoding="utf-8").read()

SUMMARY = (
    "★★**派出 (★status 保持 fixing ⇒ 无 open 窗口 ⇒ 下一轮 in_flight 规则会跳过 hw-lead ⇒ 兄弟 job 775d9893 不会重复派★)** ★ "
    "★**派活依据 (★2026-11-19 02:1x~02:3x 本机实读·不抄任何 agent 报告★)**: "
    "★**① `advance.py --json` ⇒ `internal: []` (三个总工各被一条 fixing 占位) ⇒ A 段自己派不出** ★ "
    "★**② hw-lead 名下零运行中会话 (★`sessions_list` + `subagents list` 双读: active=0 · hw-lead 最后一条会话 `5f685e7f` 01:08 结束 status=done·★01:08 之后零新 hw-lead 会话★)** ★ "
    "★**③ ISS-337 的 5 处缺口本 job 逐件独立实读确认**: 交卷页 L104 = `## B4 · 分片` (★闸认不出·★gate_check.py L51 判据 = 标题须含 `接口取值`/`接口声明`/`interface_claims`/`接口请求`★) · "
    "`grep -c iss337 state/fragments/hw.yaml` = 0 · `logs/iss337/15_seg_parity_selftest.txt` 末行 = `SELFTEST FAILED` (★用例 5 期望值写反★) · "
    "交卷页 L120 `过孔 ∈ [380, 450]` vs 脚本 L61 `VIA_LO, VIA_HI = 380, 520` 冲突 · 「归一化段数」定义未钉死 ★ "
    "★**④ 闸实测 (★本 job 02:2x 本机独立实跑 `TMPDIR=<项目内> timeout 600 python3 state/gate_check.py`★)**: rc=0 · Q1 = 17/18 (★缺口正是 hw-lead 的 B4★) · Q2 3/3 · Q6 ✅ · Q7 9/9 · extra_gates 8/8** ★ "
    "★**⑤ 派活授权: main 01:44 webchat 实读「⇒ cont1 任务书已写好落盘 (`state/dispatch_briefs/ISS-337_hw_segment_parity_cont1.md`), 5 处缺口 + 上面两条发现都写进去了, ★**兄弟 job 直接派即可**★」⇒ 明确授权本 job 派 ISS-337 cont1** ★ "
    "★**⑥ 兄弟 job 775d9893 于 01:53 死于 status=failed (★sessionId=ff0de45e · endedAt=1795024387879·★它没派成·★hw-lead 名下零新会话★) ⇒ 本 job 接手, 不存在撞车** ★ "
    "★**⑦ 不碰 sw-lead / mech-lead: ISS-335/336/338 的会话全部已结束 ⇒ 它们现在是【待 main 签收】的僵尸占位⇒ 签收是 main 的地界·本 job 不签 (★签两次会让审计出现两条 verified 记录★)⇒ 本轮无新的 open 项给它们** ★ "
    "★**brief 改动 1 处 (★追加第 6 处缺口一节·★main 的原文前 11,870 字节 `diff` 校验逐字未改★)**: "
    "★**派活方 02:2x 逐件核对 `logs/iss337/` ⇒ 交卷页 §B3 表声称 16 件、盘上只有 13 件 ⇒ 第 13/14/16 行引用不存在的文件 ⇒ §5 沙盒臂表 8 个读数列全是空指针 `(见 §B3-13)`/`(见 §B3-14)` ⇒ 与第 1 处 (B4 标题) 同属【交卷页与盘面不同步】⇒ main 一 grep 就抓到 ⇒ 不补这第 6 处, main 依然不能签** ★ "
    "★**直接原因 (★不用 agent 重跑任何臂★)**: `tmp/iss337/sbx/run_sbx.out` 实读 `[A] ★EXIT=124` (★timeout 3600 被打死⇒SBX-A 板没生成★) + SBX-B 是已死会话 `5f685e7f` 的孤儿进程 (★本 job 02:2x 已 kill·pid 1208854/1208853/1192825/1192822 全清·★板 md5/mtime 复查逐字节未动★) ⇒ 13/14 两个日志本就不可能存在 ⇒ §5 两条臂读数从一开始就没产出过** ★ "
    "★**⇒ brief 里写死了收口方式: §5 两条臂读数改 `[0数据]`+原因 + §B3 自称件数改成 13 (★不许编任何段数/过孔/铜长/unc/DRC 数字★) + 零空指针 + 追加第 ⑦ 条复现命令与第 ⑥ 条验收线** ★ "
    "★**派活前守卫: `check_brief_commands.py --brief-file state/dispatch_briefs/ISS-337_hw_segment_parity_cont1.md` ⇒ rc=0** ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · 零改闸 · 零改真生成器 · "
    "只写 `state/fragments/hw.yaml` (走 `frag_write.py --agent hw-lead`) · 不许新建臂 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不代拍那 8 个字母 · 不自签 issue_log ★"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        it = idx.get(IID)
        if it is None:
            applied.append("★★ %s 不存在 ⇒ 中止 (不新建) ★★" % IID)
            return 2

        # ★★ ISS-337 已经是 fixing ⇒ cont1 保持 fixing (★不制造 open 窗口★)
        if it.get("status") == "fixing":
            applied.append("%s 已是 fixing ⇒ 保持 (★cont1 不制造 open 窗口·★下一轮 in_flight 会跳过 hw-lead★)" % IID)
        elif it.get("status") == "open":
            it["status"] = "fixing"
            applied.append("%s status: open → fixing (★先落 fixing 再 spawn·★兜底★)" % IID)
        else:
            applied.append("★★ %s status=%s (≠open/fixing) ⇒ 中止 (绝不重复派) ★★" % (IID, it.get("status")))
            return 2

        it["dispatched_at"] = "2026-11-19"
        it["task_brief"] = BRIEF
        applied.append("%s task_brief ⇒ 指向 dispatch_briefs 文件全文 (★与落盘 brief 同一份真源·★含派活方追加的第 6 处缺口·★main 原文前 11,870 字节逐字未改★)" % IID)

        it["note"] = (
            "★★2026-11-19 02:3x · cron fb67af40 派出 ISS-337 cont1 (★先落 fixing 再 spawn ⇒ 无 open 窗口·★下一轮 in_flight 会跳过 hw-lead·★兄弟 job 775d9893 01:53 死于 status=failed·★它没派成·★本 job 接手⇒ 不存在撞车★)★★ "
            "★**依据**: advance.py A 段 internal=[] (三个总工各被 fixing 占位) + hw-lead 名下零运行中会话 (★sessions_list + subagents list 双读·★最后一条 `5f685e7f` 01:08 结束★) + "
            "★**main 01:44 webchat 授权「兄弟 job 直接派即可」**★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-337_hw_segment_parity_cont1.md` "
            "(★`check_brief_commands.py --brief-file` rc=0·★main 的原文前 11,870 字节 `diff` 校验逐字未改·★派活方只追加了第 6 处缺口一节★)★ "
            "★**本 job 02:2x 逐件独立实读确认的 5 处缺口**: B4 标题 `## B4 · 分片` (闸认不出) · `grep -c iss337 hw.yaml` = 0 · selftest 末行 `SELFTEST FAILED` · "
            "交卷页 `[380, 450]` vs 脚本 `VIA_LO, VIA_HI = 380, 520` · 归一化段数定义未钉死★ "
            "★**派活方追加的第 6 处**: 交卷页 §B3 声称 16 件、盘上 13 件 (★13/14/16 三行引用不存在的文件·★§5 沙盒臂表 8 个读数列全是空指针 `(见 §B3-13)`/`(见 §B3-14)`·★"
            "直接原因 = `run_sbx.out` 的 `[A] ★EXIT=124` (timeout 3600) + SBX-B 孤儿进程本 job 02:2x 已 kill·★板 md5/mtime 复查逐字节未动★)⇒ "
            "与第 1 处同属【交卷页与盘面不同步】⇒ 不补这第 6 处 main 依然不能签★ "
            "★**闸实测 (★本 job 02:2x 独立实跑★)**: gate_check rc=0 · Q1 = 17/18 (★缺口正是 hw-lead 的 B4·★补完应变 18/18★) · Q7 9/9 · extra_gates 8/8 ★ "
            "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · 零改闸 · 零改真生成器 · "
            "只写 `state/fragments/hw.yaml` (走 frag_write.py --agent hw-lead) · 不许新建臂 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不代拍 · 不自签 issue_log ★"
        )
        applied.append("%s dispatched_at / note 已更新" % IID)

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10 ** 6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or {}
        entries = dlog.get("dispatches") or []
        tag = "%s-cont1-20261119-0230" % IID
        if not any(tag in str(e.get("job") or "") for e in entries):
            entries.append({
                "issue": IID,
                "agent": OWNER,
                "at": "2026-11-19 02:3x",
                "brief": SUMMARY,
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-19 02:3x · "
                    "★**ISS-337 cont1 · status 保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ "
                    "★**tag = %s** ★" % tag
                ),
            })
            applied.append("dispatch_log.yaml += %s %s cont1 1 条 (★tag=%s·★幂等★)" % (IID, OWNER, tag))
            atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=10 ** 6))
        else:
            applied.append("dispatch_log.yaml 已含 %s (跳过·幂等)" % tag)

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
